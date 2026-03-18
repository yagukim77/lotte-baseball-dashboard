import os
import streamlit as st
import pandas as pd
import plotly.express as px

from analysis.team_stats import team_attack_power
from analysis.game_simulator import simulate_game
from analysis.live_graph import build_live_win_history
from analysis.live_tuner import tune_live_win_prob
from analysis.probable_starter_matcher import get_probable_starters
from analysis.war_model import calculate_batter_war, calculate_team_war
from analysis.team_elo import calculate_team_elo, get_team_elo
from analysis.lineup_model import lineup_attack_score
from analysis.fan_features import short_game_comment, explain_prediction
from analysis.tuned_ai_model import build_tuned_prediction
from crawlers.live_score import get_lotte_live_game

st.set_page_config(page_title="롯데 AI 야구 플랫폼", layout="wide")

@st.cache_data(ttl=600)
def load_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")
st.caption("튜닝 최종판 · 선발투수 fallback · 팀별 ELO · 상대강도 반영 · 홈/원정/구장/요일 반영")

menu = st.sidebar.selectbox(
    "메뉴",
    [
        "홈",
        "실시간 경기 AI",
        "오늘 경기 브리핑",
        "KBO 순위",
        "선수 OPS",
        "WAR 분석",
        "최근 경기",
        "경기 일정",
        "월간 일정",
        "팀 전력 비교",
        "팀 ELO",
        "라인업 AI",
        "시즌 예측"
    ]
)

if menu == "홈":
    st.header("오늘 경기 AI 분석")

    schedule = load_csv("data/schedule.csv")
    if schedule.empty:
        st.info("schedule.csv 데이터가 없습니다.")
    else:
        today = schedule.head(1).iloc[0]

        home = str(today["home"]).strip()
        away = str(today["away"]).strip()
        season_type = str(today["season_type"]).strip() if "season_type" in schedule.columns else ""
        game_date = str(today["date"]).strip() if "date" in schedule.columns else ""
        stadium = str(today["stadium"]).strip() if "stadium" in schedule.columns else ""

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            game_date=game_date,
            stadium=stadium,
            home_starter=home_starter,
            away_starter=away_starter
        )

        st.subheader(f"{away} vs {home} {season_type}")

        c1, c2 = st.columns(2)
        c1.metric(f"{away} 승률", f"{pred['away_prob']*100:.1f}%")
        c2.metric(f"{home} 승률", f"{pred['home_prob']*100:.1f}%")

        st.write(f"{away} 선발: {away_starter if away_starter else '팀 선발 평균치 적용'}")
        st.write(f"{home} 선발: {home_starter if home_starter else '팀 선발 평균치 적용'}")

        st.subheader("예상 스코어")
        st.write(f"{away} {pred['away_score']:.1f} : {home} {pred['home_score']:.1f}")

        st.subheader("핵심 지표")
        x1, x2, x3, x4 = st.columns(4)
        x1.metric(f"{away} 공격력", pred["away_attack"])
        x2.metric(f"{home} 공격력", pred["home_attack"])
        x3.metric(f"{away} ELO", pred["away_elo"])
        x4.metric(f"{home} ELO", pred["home_elo"])

        y1, y2, y3, y4 = st.columns(4)
        y1.metric(f"{away} 최근폼", pred["away_form"]["strength_score"])
        y2.metric(f"{home} 최근폼", pred["home_form"]["strength_score"])
        y3.metric("구장 보정", pred["park_factor"])
        y4.metric("요일 보정", pred["weekday_factor"])

        st.info(
            explain_prediction(
                pred["home_prob"],
                pred["away_prob"],
                pred["home_attack"],
                pred["away_attack"],
                pred["home_elo"],
                pred["away_elo"]
            )
        )

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

        lotte_is_home = home == "롯데"
        opp_team = away if lotte_is_home else home
        lotte_score = home_score if lotte_is_home else away_score
        opp_score = away_score if lotte_is_home else home_score

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            home_starter=home_starter,
            away_starter=away_starter
        )

        pre_prob = pred["home_prob"] if lotte_is_home else pred["away_prob"]

        live_prob = tune_live_win_prob(
            base_prob=pre_prob,
            lotte_score=lotte_score,
            opp_score=opp_score,
            status=status,
            is_home=lotte_is_home
        )

        st.subheader(f"{away} vs {home}")
        st.write(f"현재 상태: {status}")
        st.write(f"스코어: {away} {away_score} : {home} {home_score}")

        c1, c2, c3 = st.columns(3)
        c1.metric("롯데 실시간 승률", f"{live_prob*100:.1f}%")
        c2.metric("프리게임 승률", f"{pre_prob*100:.1f}%")
        c3.metric("현재 점수차", lotte_score - opp_score)

        st.progress(float(live_prob))

        history_df = build_live_win_history(live_prob, status)
        fig = px.line(history_df, x="inning", y="win_prob", markers=True, title="이닝별 예상 승률 변화")
        st.plotly_chart(fig, use_container_width=True)

        st.info(short_game_comment(live_prob, status, lotte_score - opp_score))

elif menu == "오늘 경기 브리핑":
    st.header("📋 오늘 경기 브리핑")

    schedule = load_csv("data/schedule.csv")
    if schedule.empty:
        st.info("schedule.csv 데이터가 없습니다.")
    else:
        today = schedule.head(1).iloc[0]

        home = str(today["home"]).strip()
        away = str(today["away"]).strip()
        game_date = str(today["date"]).strip() if "date" in schedule.columns else ""
        stadium = str(today["stadium"]).strip() if "stadium" in schedule.columns else ""

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            game_date=game_date,
            stadium=stadium,
            home_starter=home_starter,
            away_starter=away_starter
        )

        st.subheader(f"{away} vs {home}")
        st.write(f"{away} 선발: {away_starter if away_starter else '팀 선발 평균치 적용'}")
        st.write(f"{home} 선발: {home_starter if home_starter else '팀 선발 평균치 적용'}")
        st.write(f"{away} 승률: {pred['away_prob']*100:.1f}%")
        st.write(f"{home} 승률: {pred['home_prob']*100:.1f}%")
        st.write(f"예상 스코어: {away} {pred['away_score']:.1f} : {home} {pred['home_score']:.1f}")

        a, b, c, d = st.columns(4)
        a.metric(f"{away} 최근폼", pred["away_form"]["strength_score"])
        b.metric(f"{home} 최근폼", pred["home_form"]["strength_score"])
        c.metric(f"{away} 선발 ERA", pred["away_starter_era"])
        d.metric(f"{home} 선발 ERA", pred["home_starter_era"])

elif menu == "KBO 순위":
    st.header("KBO 순위")
    df = load_csv("data/kbo_standings.csv")
    if df.empty:
        st.info("kbo_standings.csv 데이터가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "선수 OPS":
    st.header("선수 OPS")
    df = load_csv("data/players_stats.csv")
    if df.empty:
        st.info("players_stats.csv 데이터가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)
        if {"player", "ops"}.issubset(df.columns):
            fig = px.bar(df.sort_values("ops", ascending=False).head(20), x="player", y="ops", color="team")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "WAR 분석":
    st.header("WAR 분석")
    try:
        batter_war = calculate_batter_war()
        team_war = calculate_team_war()

        st.subheader("선수 WAR TOP 15")
        st.dataframe(batter_war.head(15), use_container_width=True)
        fig1 = px.bar(batter_war.head(15), x="player", y="war", color="team")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("팀 WAR")
        st.dataframe(team_war, use_container_width=True)
        fig2 = px.bar(team_war, x="team", y="war")
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.info(f"WAR 데이터 오류: {e}")

elif menu == "최근 경기":
    st.header("최근 경기")
    df = load_csv("data/games.csv")
    if df.empty:
        st.info("games.csv 데이터가 없습니다.")
    else:
        st.dataframe(df.tail(10), use_container_width=True)

elif menu == "경기 일정":
    st.header("경기 일정")
    df = load_csv("data/schedule.csv")
    if df.empty:
        st.info("schedule.csv 데이터가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "월간 일정":
    st.header("월간 일정")
    df = load_csv("data/monthly_schedule.csv")
    if df.empty:
        st.info("monthly_schedule.csv 데이터가 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)
        lotte_df = df[(df["home"] == "롯데") | (df["away"] == "롯데")]
        st.subheader("롯데 일정")
        st.dataframe(lotte_df, use_container_width=True)

elif menu == "팀 전력 비교":
    st.header("팀 전력 비교")

    players_df = load_csv("data/players_stats.csv")
    if players_df.empty or "team" not in players_df.columns:
        st.info("팀 비교용 데이터가 없습니다.")
    else:
        teams = sorted(players_df["team"].dropna().unique())
        teamA = st.selectbox("팀A", teams)
        teamB = st.selectbox("팀B", teams)

        teamA_home = st.checkbox(f"{teamA} 홈 기준", value=True)
        teamB_home = st.checkbox(f"{teamB} 홈 기준", value=False)

        teamA_lineup_players = st.multiselect(f"{teamA} 라인업 수동 입력", sorted(players_df[players_df["team"] == teamA]["player"].astype(str).unique()))
        teamB_lineup_players = st.multiselect(f"{teamB} 라인업 수동 입력", sorted(players_df[players_df["team"] == teamB]["player"].astype(str).unique()))

        lineup_boost_a = lineup_attack_score(teamA_lineup_players, is_home=teamA_home) if teamA_lineup_players else None
        lineup_boost_b = lineup_attack_score(teamB_lineup_players, is_home=teamB_home) if teamB_lineup_players else None

        pred = build_tuned_prediction(
            home_team=teamA if teamA_home else teamB,
            away_team=teamB if teamA_home else teamA,
            lineup_boost_home=lineup_boost_a if teamA_home else lineup_boost_b,
            lineup_boost_away=lineup_boost_b if teamA_home else lineup_boost_a
        )

        compare_df = pd.DataFrame({
            "team": [pred["away_team"], pred["home_team"]],
            "attack": [pred["away_attack"], pred["home_attack"]],
            "elo": [pred["away_elo"], pred["home_elo"]],
            "win_prob": [pred["away_prob"], pred["home_prob"]],
        })

        st.dataframe(compare_df, use_container_width=True)

        fig = px.bar(compare_df, x="team", y="attack", title="공격력 비교")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric(f"{pred['away_team']} 승률", f"{pred['away_prob']*100:.1f}%")
        c2.metric(f"{pred['home_team']} 승률", f"{pred['home_prob']*100:.1f}%")

elif menu == "팀 ELO":
    st.header("팀 ELO")
    elo_df = calculate_team_elo()

    if elo_df.empty:
        st.info("ELO 계산용 데이터가 없습니다.")
    else:
        st.dataframe(elo_df, use_container_width=True)
        fig = px.bar(elo_df, x="team", y="elo")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("롯데 ELO", get_team_elo("롯데"))

elif menu == "라인업 AI":
    st.header("라인업 AI")

    players_df = load_csv("data/players_stats.csv")
    if players_df.empty or "player" not in players_df.columns:
        st.info("라인업용 선수 데이터가 없습니다.")
    else:
        team = st.selectbox("팀 선택", sorted(players_df["team"].dropna().unique()))
        is_home = st.checkbox("홈 경기 기준", value=True)
        player_list = sorted(players_df[players_df["team"] == team]["player"].astype(str).unique())

        selected = st.multiselect("오늘 라인업 9명 선택", player_list, default=player_list[:9] if len(player_list) >= 9 else player_list)
        score = lineup_attack_score(selected, is_home=is_home)

        st.metric("라인업 공격력", score)

        if selected:
            selected_df = players_df[players_df["player"].isin(selected)]
            st.dataframe(selected_df, use_container_width=True)

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
        st.info(f"시즌 예측 오류: {e}")
