import streamlit as st
import pandas as pd
import plotly.express as px

from analysis.keywords import extract_keywords
from analysis.ai_model import predict_win, predict_score
from analysis.elo_rating import calculate_elo
from analysis.team_stats import team_attack_power, recent_form
from analysis.simulator import simulate_game


st.set_page_config(
    page_title="롯데 AI 야구 플랫폼",
    layout="wide"
)

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")

menu = st.sidebar.selectbox(
    "메뉴",
    [
        "홈",
        "뉴스 분석",
        "KBO 순위",
        "선수 OPS",
        "최근 경기",
        "경기 일정",
        "AI 분석",
        "팀 전력 비교"
    ]
)

# 홈

if menu == "홈":

    st.header("오늘 경기 AI 분석")

    try:

        schedule = pd.read_csv("data/schedule.csv")

        today = schedule.head(1)

        home = today.iloc[0]["home"]
        away = today.iloc[0]["away"]

        st.subheader(f"{away} vs {home}")

        a_attack = team_attack_power(away)
        b_attack = team_attack_power(home)

        sim = simulate_game(a_attack, b_attack)

        col1, col2 = st.columns(2)

        col1.metric(
            away + " 승률",
            f"{sim['A_win']*100:.1f}%"
        )

        col2.metric(
            home + " 승률",
            f"{sim['B_win']*100:.1f}%"
        )

        st.subheader("예상 스코어")

        st.write(
            f"{away} {sim['A_score']:.1f} : {home} {sim['B_score']:.1f}"
        )

    except:

        st.write("경기 데이터 없음")

    elo = calculate_elo()

    st.metric("롯데 전력지수(ELO)", elo)

# 뉴스

elif menu == "뉴스 분석":

    st.header("롯데 뉴스")

    try:

        df = pd.read_csv("data/news.csv")

        st.dataframe(df)

        keywords = extract_keywords(df["title"])

        kw_df = pd.DataFrame(
            keywords,
            columns=["keyword", "count"]
        )

        fig = px.bar(
            kw_df,
            x="keyword",
            y="count",
            height=400
        )

        st.plotly_chart(fig)

    except:

        st.write("뉴스 데이터 없음")

# 순위

elif menu == "KBO 순위":

    st.header("KBO 순위")

    try:

        df = pd.read_csv("data/kbo_standings.csv")

        st.dataframe(df)

    except:

        st.write("순위 데이터 없음")

# OPS

elif menu == "선수 OPS":

    st.header("롯데 선수 OPS")

    try:

        df = pd.read_csv("data/players_stats.csv")

        st.dataframe(df)

        fig = px.bar(
            df,
            x="player",
            y="ops",
            height=300
        )

        st.plotly_chart(fig)

        top = df.sort_values(
            "ops",
            ascending=False
        ).head(10)

        st.subheader("OPS TOP10")

        st.dataframe(top)

    except:

        st.write("선수 데이터 없음")

# 최근 경기

elif menu == "최근 경기":

    st.header("롯데 최근 경기")

    try:

        df = pd.read_csv("data/games.csv")

        last10 = df.tail(10)

        st.dataframe(last10)

        wins, loses, avg_score, avg_allowed = recent_form()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("최근10경기 승", wins)
        col2.metric("최근10경기 패", loses)
        col3.metric("평균 득점", f"{avg_score:.1f}")
        col4.metric("평균 실점", f"{avg_allowed:.1f}")

    except:

        st.write("경기 데이터 없음")

# 경기 일정

elif menu == "경기 일정":

    st.header("롯데 경기 일정")

    try:

        df = pd.read_csv("data/schedule.csv")

        st.dataframe(df)

    except:

        st.write("일정 데이터 없음")

# AI 분석

elif menu == "AI 분석":

    st.header("AI 경기 분석")

    win = predict_win()

    st.metric(
        "AI 승률",
        f"{win*100:.1f}%"
    )

    score = predict_score()

    st.subheader(score)

    elo = calculate_elo()

    st.metric("ELO", elo)

# 팀 전력 비교

elif menu == "팀 전력 비교":

    st.header("KBO 팀 전력 비교")

    df = pd.read_csv("data/players_stats.csv")

    teams = df["team"].unique()

    teamA = st.selectbox("팀A", teams)
    teamB = st.selectbox("팀B", teams)

    a_attack = team_attack_power(teamA)
    b_attack = team_attack_power(teamB)

    col1, col2 = st.columns(2)

    col1.metric(teamA + " 공격력", a_attack)
    col2.metric(teamB + " 공격력", b_attack)

    sim = simulate_game(a_attack, b_attack)

    st.subheader("AI 승률")

    st.write(teamA, f"{sim['A_win']*100:.1f}%")
    st.write(teamB, f"{sim['B_win']*100:.1f}%")
