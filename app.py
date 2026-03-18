import streamlit as st
import pandas as pd
import plotly.express as px

from analysis.keywords import extract_keywords
from analysis.ai_model import predict_win, predict_score
from analysis.elo_rating import calculate_elo
from analysis.team_stats import team_attack_power, recent_form
from analysis.game_simulator import simulate_game
from analysis.live_win_model import pregame_win_prob, live_win_prob
from services.data_loader import safe_read_csv

try:
    from crawlers.live_score import get_lotte_live_game
except Exception:
    def get_lotte_live_game():
        return None

st.set_page_config(page_title="롯데 AI 야구 플랫폼", layout="wide")

@st.cache_data(ttl=600)
def load_csv(path):
    return pd.read_csv(path)


def show_youtube_links(team_a: str, team_b: str):
    queries = build_highlight_queries(team_a, team_b)
    st.subheader("하이라이트 바로가기")
    for q in queries:
        st.markdown(f"- [{q}]({build_youtube_search_url(q)})")


st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")

menu = st.sidebar.selectbox(
    "메뉴",
    [
        "홈",
        "실시간 경기 AI",
        "뉴스 분석",
        "KBO 순위",
        "선수 OPS",
        "WAR 분석",
        "최근 경기",
        "경기 일정",
        "월간 일정",
        "AI 분석",
        "팀 전력 비교",
        "팀 ELO",
        "라인업 AI",
        "시즌 예측",
    ]
)

if menu == "홈":
    st.header("오늘 경기 AI 분석")
    try:
        df = load_csv("data/schedule.csv")
        today = df.head(1)
        home = today.iloc[0]["home"]
        away = today.iloc[0]["away"]
        season_type = today.iloc[0]["season_type"] if "season_type" in today.columns else ""
        st.subheader(f"{away} vs {home} {season_type}")

        a_attack = team_attack_power(away)
        b_attack = team_attack_power(home)
        away_starter = ""
        home_starter = ""
        try:
            starters = load_csv("data/probable_starters.csv")
            target = starters[(starters["away"] == away) & (starters["home"] == home)]
            if not target.empty:
                away_starter = str(target.iloc[0].get("away_starter", ""))
                home_starter = str(target.iloc[0].get("home_starter", ""))
        except Exception:
            pass

        a_attack_adj = adjust_attack_by_starter(a_attack, home_starter)
        b_attack_adj = adjust_attack_by_starter(b_attack, away_starter)

        sim = simulate_game(a_attack_adj, b_attack_adj)
        col1, col2 = st.columns(2)
        col1.metric(away + " 승률", f"{sim['A_win']*100:.1f}%")
        col2.metric(home + " 승률", f"{sim['B_win']*100:.1f}%")

        st.write(f"{away} 선발: {away_starter if away_starter else '미정'}")
        st.write(f"{home} 선발: {home_starter if home_starter else '미정'}")
        st.subheader("예상 스코어")
        st.write(f"{away} {sim['A_score']:.1f} : {home} {sim['B_score']:.1f}")
        show_youtube_links(away, home)
    except Exception as e:
        st.info(f"경기 데이터 없음: {e}")

    elo = calculate_elo()
    st.metric("롯데 전력지수(ELO)", elo)

elif menu == "실시간 경기 AI":
    st.header("🔥 실시간 경기 AI")
    game = get_lotte_live_game()
    if not game:
        st.info("현재 롯데 실시간 경기 데이터가 없습니다.")
    else:
        away = game["away"]
        home = game["home"]
        away_score = int(game["away_score"])
        home_score = int(game["home_score"])
        status = game["status"]

        st.subheader(f"{away} vs {home}")
        st.write(f"현재 상태: {status}")
        st.write(f"스코어: {away} {away_score} : {home} {home_score}")

        lotte_is_away = away == "롯데"
        opp_team = home if lotte_is_away else away
        lotte_score = away_score if lotte_is_away else home_score
        opp_score = home_score if lotte_is_away else away_score

        lotte_attack = team_attack_power("롯데")
        opp_attack = team_attack_power(opp_team)
        lotte_elo = get_team_elo("롯데")
        opp_elo = get_team_elo(opp_team)

        pre_p = pregame_win_prob(lotte_attack, opp_attack, lotte_elo, opp_elo)
        live_p = live_win_prob(pre_p, lotte_score, opp_score, status)

        col1, col2, col3 = st.columns(3)
        col1.metric("롯데 실시간 승률", f"{live_p*100:.1f}%")
        col2.metric("프리게임 승률", f"{pre_p*100:.1f}%")
        col3.metric("현재 점수차", lotte_score - opp_score)
        st.progress(float(live_p))

        history_df = build_live_win_history(live_p, status)
        fig = px.line(history_df, x="inning", y="win_prob", markers=True, title="이닝별 예상 승률 변화")
        st.plotly_chart(fig, use_container_width=True)

        if live_p >= 0.7:
            st.success("현재 흐름은 롯데 우세")
        elif live_p <= 0.3:
            st.error("현재 흐름은 상대팀 우세")
        else:
            st.warning("아직 승부가 팽팽합니다.")

        show_youtube_links(away, home)

elif menu == "뉴스 분석":
    st.header("롯데 뉴스")
    try:
        df = load_csv("data/news.csv")
        st.dataframe(df, use_container_width=True)
        keywords = extract_keywords(df["title"])
        kw_df = pd.DataFrame(keywords, columns=["keyword", "count"])
        fig = px.bar(kw_df, x="keyword", y="count")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"뉴스 없음: {e}")

elif menu == "KBO 순위":
    st.header("KBO 순위")
    try:
        df = load_csv("data/kbo_standings.csv")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info(f"데이터 없음: {e}")

elif menu == "선수 OPS":
    st.header("롯데 선수 OPS")
    try:
        df = load_csv("data/players_stats.csv")
        st.dataframe(df, use_container_width=True)
        fig = px.bar(df, x="player", y="ops", color="team")
        st.plotly_chart(fig, use_container_width=True)
        top = df.sort_values("ops", ascending=False).head(10)
        st.subheader("OPS TOP10")
        st.dataframe(top, use_container_width=True)
    except Exception as e:
        st.info(f"데이터 없음: {e}")

elif menu == "WAR 분석":
    st.header("📊 WAR 분석")
    try:
        batter_war = calculate_batter_war()
        team_war = calculate_team_war()
        st.subheader("선수 WAR TOP 15")
        st.dataframe(batter_war.head(15), use_container_width=True)
        fig1 = px.bar(batter_war.head(15), x="player", y="war", color="team", title="선수 WAR TOP 15")
        st.plotly_chart(fig1, use_container_width=True)
        st.subheader("팀 WAR 순위")
        st.dataframe(team_war, use_container_width=True)
        fig2 = px.bar(team_war, x="team", y="war", title="팀 WAR")
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.info(f"WAR 데이터 없음: {e}")

elif menu == "최근 경기":
    st.header("최근 경기")
    try:
        df = load_csv("data/games.csv")
        last10 = df.tail(10)
        st.dataframe(last10, use_container_width=True)
        wins, loses, avg_score, avg_allowed = recent_form()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("승", wins)
        col2.metric("패", loses)
        col3.metric("득점", f"{avg_score:.1f}")
        col4.metric("실점", f"{avg_allowed:.1f}")
    except Exception as e:
        st.info(f"데이터 없음: {e}")

elif menu == "경기 일정":
    st.header("경기 일정")
    try:
        df = load_csv("data/schedule.csv")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info(f"데이터 없음: {e}")

elif menu == "월간 일정":
    st.header("월간 일정")
    try:
        df = load_csv("data/monthly_schedule.csv")
        st.dataframe(df, use_container_width=True)
        lotte = df[(df["home"] == "롯데") | (df["away"] == "롯데")]
        st.subheader("롯데 일정")
        st.dataframe(lotte, use_container_width=True)
    except Exception as e:
        st.info(f"데이터 없음: {e}")

elif menu == "AI 분석":
    st.header("AI 분석")
    try:
        win = predict_win()
        score = predict_score()
        st.metric("승률", f"{win*100:.1f}%")
        st.write(score)
    except Exception as e:
        st.info(f"AI 분석 오류: {e}")

elif menu == "팀 전력 비교":
    st.header("⚔️ 팀 전력 비교")
    df = load_csv("data/players_stats.csv")
    teams = sorted(df["team"].dropna().unique())
    teamA = st.selectbox("팀A", teams)
    teamB = st.selectbox("팀B", teams)
    a_attack = team_attack_power(teamA)
    b_attack = team_attack_power(teamB)
    sim = simulate_game(a_attack, b_attack)
    compare_df = pd.DataFrame({"team": [teamA, teamB], "attack": [a_attack, b_attack], "win_prob": [sim["A_win"], sim["B_win"]]})
    st.dataframe(compare_df, use_container_width=True)
    fig = px.bar(compare_df, x="team", y="attack", title="팀 공격력 비교")
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric(f"{teamA} 승률", f"{sim['A_win']*100:.1f}%")
    col2.metric(f"{teamB} 승률", f"{sim['B_win']*100:.1f}%")

elif menu == "팀 ELO":
    st.header("📈 팀 ELO 랭킹")
    elo_df = calculate_team_elo_table()
    st.dataframe(elo_df, use_container_width=True)
    if not elo_df.empty:
        fig = px.bar(elo_df, x="team", y="elo", title="KBO 팀 ELO")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "라인업 AI":
    st.header("🧠 라인업 AI")
    df = load_csv("data/players_stats.csv")
    teams = sorted(df["team"].dropna().unique())
    team = st.selectbox("팀 선택", teams)

    default_lineup = get_default_lineup(team)
    st.write("기본 추천 라인업")
    st.write(", ".join(default_lineup) if default_lineup else "데이터 없음")

    lineup_strength = estimate_lineup_strength(team, default_lineup)
    base_attack = team_attack_power(team)
    st.metric("라인업 공격력", lineup_strength)
    st.metric("기본 팀 공격력", base_attack)

    lineup_df = df[df["team"] == team].copy().sort_values("ops", ascending=False).head(9)
    if not lineup_df.empty:
        fig = px.bar(lineup_df, x="player", y="ops", title=f"{team} 예상 주전 라인업 OPS")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "시즌 예측":
    st.header("시즌 예측")
    try:
        from analysis.season_predictor import predict_season
        df = predict_season()
        st.dataframe(df, use_container_width=True)
        lotte = df[df["team"] == "롯데"]
        if not lotte.empty:
            st.metric("롯데 예상 순위", int(lotte.iloc[0]["pred_rank"]))
    except Exception as e:
        st.info(f"데이터 없음: {e}")
