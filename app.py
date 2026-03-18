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

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")

menu = st.sidebar.selectbox(
    "메뉴",
    [
        "홈",
        "실시간 경기 AI",
        "뉴스 분석",
        "KBO 순위",
        "선수 OPS",
        "최근 경기",
        "경기 일정",
        "월간 일정",
        "AI 분석",
        "팀 전력 비교",
        "시즌 예측"
    ]
)

if menu == "홈":
    st.header("오늘 경기 AI 분석")

    schedule = safe_read_csv("data/kbo_schedule.csv", ["date", "away", "home", "season_type"])

    if schedule.empty:
        st.info("경기 일정 데이터가 없습니다.")
    else:
        today = schedule.head(1)
        home = str(today.iloc[0].get("home", ""))
        away = str(today.iloc[0].get("away", ""))
        season_type = str(today.iloc[0].get("season_type", ""))

        st.subheader(f"{away} vs {home} {season_type}")

        a_attack = team_attack_power(away) if away else 4.5
        b_attack = team_attack_power(home) if home else 4.5

        sim = simulate_game(a_attack, b_attack)

        col1, col2 = st.columns(2)
        col1.metric(f"{away} 승률", f"{sim['A_win']*100:.1f}%")
        col2.metric(f"{home} 승률", f"{sim['B_win']*100:.1f}%")

        st.subheader("예상 스코어")
        st.write(f"{away} {sim['A_score']:.1f} : {home} {sim['B_score']:.1f}")

    st.metric("롯데 전력지수(ELO)", calculate_elo())

elif menu == "실시간 경기 AI":
    st.header("🔥 실시간 경기 AI")

    game = get_lotte_live_game()

    if not game:
        st.info("현재 롯데 실시간 경기 데이터가 없습니다.")
    else:
        away = game.get("away", "")
        home = game.get("home", "")
        away_score = int(game.get("away_score", 0))
        home_score = int(game.get("home_score", 0))
        status = game.get("status", "경기전")

        st.subheader(f"{away} vs {home}")
        st.write(f"현재 상태: {status}")
        st.write(f"스코어: {away} {away_score} : {home} {home_score}")

        lotte_is_away = away == "롯데"
        opp_team = home if lotte_is_away else away

        lotte_score = away_score if lotte_is_away else home_score
        opp_score = home_score if lotte_is_away else away_score

        lotte_attack = team_attack_power("롯데")
        opp_attack = team_attack_power(opp_team) if opp_team else 4.5

        pre_p = pregame_win_prob(
            base_attack=lotte_attack,
            opp_attack=opp_attack,
            lotte_elo=calculate_elo(),
            opp_elo=1500
        )

        live_p = live_win_prob(pre_p, lotte_score, opp_score, status)

        st.metric("롯데 실시간 승률", f"{live_p*100:.1f}%")
        st.progress(float(live_p))

elif menu == "뉴스 분석":
    st.header("롯데 뉴스")

    news = safe_read_csv("data/news.csv", ["title"])

    if news.empty:
        st.info("뉴스 데이터가 없습니다.")
    else:
        st.dataframe(news, use_container_width=True)

        if "title" in news.columns:
            keywords = extract_keywords(news["title"].dropna())
            kw_df = pd.DataFrame(keywords, columns=["keyword", "count"])

            if not kw_df.empty:
                fig = px.bar(kw_df, x="keyword", y="count", height=400)
                st.plotly_chart(fig, use_container_width=True)

elif menu == "KBO 순위":
    st.header("KBO 순위")

    standings = safe_read_csv("data/kbo_standings.csv")

    if standings.empty:
        st.info("순위 데이터가 없습니다.")
    else:
        st.dataframe(standings, use_container_width=True)

elif menu == "선수 OPS":
    st.header("🔥 KBO 타자 OPS 분석")

    hitters = safe_read_csv("data/players_stats.csv", ["player", "team", "avg", "hr", "rbi", "ops"])

    if hitters.empty:
        st.info("선수 데이터가 없습니다.")
    else:
        st.dataframe(hitters, use_container_width=True)

        if "ops" in hitters.columns and "player" in hitters.columns:
            fig = px.bar(hitters.sort_values("ops", ascending=False).head(20), x="player", y="ops")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "최근 경기":
    st.header("롯데 최근 경기")

    games = safe_read_csv("data/games.csv")

    if games.empty:
        st.info("최근 경기 데이터가 없습니다.")
    else:
        last10 = games.tail(10)
        st.dataframe(last10, use_container_width=True)

        try:
            wins, loses, avg_score, avg_allowed = recent_form()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("승", wins)
            col2.metric("패", loses)
            col3.metric("평균 득점", f"{avg_score:.1f}")
            col4.metric("평균 실점", f"{avg_allowed:.1f}")
        except Exception:
            pass

elif menu == "경기 일정":
    st.header("경기 일정")

    schedule = safe_read_csv("data/kbo_schedule.csv")

    if schedule.empty:
        st.info("경기 일정 데이터가 없습니다.")
    else:
        st.dataframe(schedule, use_container_width=True)

elif menu == "월간 일정":
    st.header("월간 일정")

    monthly = safe_read_csv("data/monthly_schedule.csv")

    if monthly.empty:
        st.info("월간 일정 데이터가 없습니다.")
    else:
        st.dataframe(monthly, use_container_width=True)

        if "home" in monthly.columns and "away" in monthly.columns:
            lotte = monthly[(monthly["home"] == "롯데") | (monthly["away"] == "롯데")]
            st.subheader("롯데 일정")
            st.dataframe(lotte, use_container_width=True)

elif menu == "AI 분석":
    st.header("AI 분석")

    try:
        st.metric("승률", f"{predict_win()*100:.1f}%")
        st.write(predict_score())
    except Exception:
        st.info("AI 분석 데이터를 불러오지 못했습니다.")

elif menu == "팀 전력 비교":
    st.header("⚔️ 팀 전력 비교")

    hitters = safe_read_csv("data/players_stats.csv", ["player", "team", "avg", "hr", "rbi", "ops"])

    if hitters.empty or "team" not in hitters.columns:
        st.info("팀 비교용 데이터가 없습니다.")
    else:
        teams = sorted(hitters["team"].dropna().unique())

        if len(teams) < 2:
            st.info("비교할 팀 데이터가 부족합니다.")
        else:
            teamA = st.selectbox("팀A", teams)
            teamB = st.selectbox("팀B", teams)

            a_attack = team_attack_power(teamA)
            b_attack = team_attack_power(teamB)

            sim = simulate_game(a_attack, b_attack)

            col1, col2 = st.columns(2)
            col1.metric(f"{teamA} 승률", f"{sim['A_win']*100:.1f}%")
            col2.metric(f"{teamB} 승률", f"{sim['B_win']*100:.1f}%")

elif menu == "시즌 예측":
    st.header("📈 AI 시즌 순위 예측")

    team_stats = safe_read_csv("data/team_stats.csv")

    if team_stats.empty:
        st.info("팀 스탯 데이터가 없습니다.")
    else:
        try:
            from analysis.season_predictor import predict_season
            season_df = predict_season()
            st.dataframe(season_df, use_container_width=True)
        except Exception:
            st.dataframe(team_stats, use_container_width=True)
