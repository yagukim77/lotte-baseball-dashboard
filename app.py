import streamlit as st
import pandas as pd
import plotly.express as px
import os

from analysis.ai_model import predict_win, predict_score
from analysis.elo_rating import calculate_elo
from analysis.keywords import extract_keywords


st.set_page_config(
    page_title="롯데 AI 야구 플랫폼",
    layout="wide"
)


st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")


menu = st.sidebar.selectbox(
    "메뉴 선택",
    [
        "홈",
        "뉴스 분석",
        "KBO 순위",
        "선수 OPS",
        "최근 경기",
        "AI 경기 분석"
    ]
)

# -----------------------------
# 홈
# -----------------------------

if menu == "홈":

    st.header("롯데 자이언츠 대시보드")

    win_prob = predict_win()

    st.metric(
        "AI 승리 확률",
        f"{win_prob*100:.1f}%"
    )

    score = predict_score()

    st.write("AI 예상 스코어")

    st.subheader(score)

    elo = calculate_elo()

    st.metric(
        "전력지수(ELO)",
        elo
    )


# -----------------------------
# 뉴스 분석
# -----------------------------

elif menu == "뉴스 분석":

    st.header("롯데 뉴스 분석")

    try:

        df = pd.read_csv("data/news.csv")

        st.dataframe(df)

        keywords = extract_keywords(df["title"])

        kw_df = pd.DataFrame(keywords,columns=["keyword","count"])

        fig = px.bar(
            kw_df,
            x="keyword",
            y="count",
            height=400
        )

        st.plotly_chart(fig)

    except:

        st.write("뉴스 데이터 없음")


# -----------------------------
# KBO 순위
# -----------------------------

elif menu == "KBO 순위":

    st.header("KBO 순위")

    try:

        df = pd.read_csv("data/kbo_standings.csv")

        st.dataframe(df)

    except:

        st.write("순위 데이터 없음")


# -----------------------------
# 선수 OPS
# -----------------------------

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

    except:

        st.write("선수 데이터 없음")


# -----------------------------
# 최근 경기
# -----------------------------

elif menu == "최근 경기":

    st.header("롯데 최근 경기")

    try:

        df = pd.read_csv("data/games.csv")

        last10 = df.tail(10)

        st.dataframe(last10)

        wins = len(last10[last10["result"]=="W"])

        st.metric(
            "최근 10경기 승리",
            wins
        )

    except:

        st.write("경기 데이터 없음")


# -----------------------------
# AI 경기 분석
# -----------------------------

elif menu == "AI 경기 분석":

    st.header("AI 경기 분석")

    win_prob = predict_win()

    st.metric(
        "승리 확률",
        f"{win_prob*100:.1f}%"
    )

    score = predict_score()

    st.subheader("AI 예상 스코어")

    st.write(score)

    elo = calculate_elo()

    st.metric(
        "ELO 전력지수",
        elo
    )
