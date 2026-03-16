import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np
import re
from collections import Counter

# =========================
# 페이지 설정
# =========================

st.set_page_config(
    page_title="롯데 AI 야구 플랫폼",
    layout="wide"
)

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")

# =========================
# 데이터 로드
# =========================

@st.cache_data
def load_news():
    try:
        return pd.read_csv("data/news.csv")
    except:
        return pd.DataFrame(columns=["title","link"])


@st.cache_data
def load_players():
    try:
        return pd.read_csv("data/players_stats.csv")
    except:
        return pd.DataFrame(columns=["name","ops"])


@st.cache_data
def load_schedule():
    try:
        try:
            return pd.read_csv("data/schedule.csv")
        except:
            return pd.DataFrame(columns=["date","opponent"])
    except:
        return pd.DataFrame()


@st.cache_data
def load_games():
    try:
        return pd.read_csv("data/games.csv")
    except:
        return pd.DataFrame(columns=["date","opponent","result"])


@st.cache_data
def load_standings():
    try:
        return pd.read_csv("data/kbo_standings.csv")
    except:
        return pd.DataFrame(columns=["team","win","lose","draw","rate"])


news = load_news()
players = load_players()
schedule = load_schedule()
games = load_games()
standings = load_standings()


# =========================
# 사이드 메뉴
# =========================

menu = st.sidebar.selectbox(

    "메뉴",

    [
        "대시보드",
        "뉴스",
        "선수 OPS 분석",
        "경기 일정",
        "경기 결과",
        "AI 경기 분석",
        "경기 시뮬레이터"
    ]

)


# =========================
# 대시보드
# =========================

if menu == "대시보드":

    st.header("📊 롯데 대시보드")

    if len(games) > 0:

        last10 = games.tail(10)

        wins = len(last10[last10["result"]=="승"])
        loses = len(last10[last10["result"]=="패"])
        draws = len(last10[last10["result"]=="무"])

    else:

        wins = loses = draws = 0

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("최근 10경기 승",wins)

    with col2:
        st.metric("최근 10경기 패",loses)

    with col3:
        st.metric("최근 10경기 무",draws)


    st.subheader("KBO 순위")

    st.dataframe(standings)


# =========================
# 뉴스
# =========================

if menu == "뉴스":

    st.header("📰 롯데 뉴스")

    for i,row in news.head(20).iterrows():

        st.markdown(f"[{row['title']}]({row['link']})")


    st.subheader("뉴스 키워드 분석")

    titles = news["title"].tolist()

    words=[]

    for t in titles:

        w=re.findall(r"[가-힣]{2,}",t)

        words.extend(w)

    counter=Counter(words)

    top=counter.most_common(10)

    keywords=pd.DataFrame(top,columns=["keyword","count"])

    st.dataframe(keywords)


# =========================
# 선수 OPS 분석
# =========================

if menu == "선수 OPS 분석":

    st.header("🏏 롯데 선수 OPS")

    st.dataframe(players)

    if len(players)>0:

        fig, ax = plt.subplots(figsize=(4,2))

        ax.bar(players["name"],players["ops"])

        ax.set_title("OPS")

        plt.xticks(rotation=45)

        st.pyplot(fig)



# =========================
# 경기 일정
# =========================

if menu == "경기 일정":

    st.header("📅 경기 일정")

    st.dataframe(schedule)


# =========================
# 경기 결과
# =========================

if menu == "경기 결과":

    st.header("📊 경기 결과")

    st.dataframe(games)


# =========================
# AI 분석
# =========================

if menu == "AI 경기 분석":

    st.header("🤖 AI 경기 분석")


    if len(players)>0:

        lotte_ops = players["ops"].mean()

    else:

        lotte_ops = 0.72


    opp_ops = random.uniform(0.65,0.80)


    win_prob = lotte_ops / (lotte_ops + opp_ops)

    st.metric("AI 승률 예측", round(win_prob,2))


    st.subheader("시즌 승리 그래프")

    if len(games)>0:

        games["win"]=games["result"].apply(lambda x:1 if x=="승" else 0)

        games["cum"]=games["win"].cumsum()

        games["game"]=range(1,len(games)+1)

        fig,ax=plt.subplots(figsize=(6,3))

        ax.plot(games["game"],games["cum"])

        ax.set_title("누적 승리")

        st.pyplot(fig)


# =========================
# 경기 시뮬레이터
# =========================

if menu == "경기 시뮬레이터":

    st.header("🎮 경기 시뮬레이터")

    teams = [

        "LG",
        "두산",
        "KIA",
        "삼성",
        "한화",
        "KT",
        "SSG",
        "NC",
        "키움"

    ]

    opponent = st.selectbox("상대팀 선택",teams)


    if len(players)>0:

        lotte_ops = players["ops"].mean()

    else:

        lotte_ops = 0.72


    opp_ops = random.uniform(0.65,0.80)


    prob = lotte_ops/(lotte_ops+opp_ops)


    lotte_score = int(prob*10)+random.randint(0,2)

    opp_score = int((1-prob)*10)+random.randint(0,2)


    st.subheader("AI 예상 스코어")

    col1,col2 = st.columns(2)

    with col1:
        st.metric("롯데",lotte_score)

    with col2:
        st.metric(opponent,opp_score)


    if lotte_score>opp_score:

        st.success("롯데 승리 예상")

    else:

        st.error("상대팀 승리 예상")
