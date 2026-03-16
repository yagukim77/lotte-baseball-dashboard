import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import re
from collections import Counter

from ai.elo_rating import calculate_elo
from ai.win_model import predict_win_probability
from ai.simulator import simulate_game

# 자동 새로고침 안정코드
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=600000)
except:
    pass

# sidebar 메뉴 CSS
st.markdown("""
<style>

.menu-item {
padding:10px;
font-size:18px;
border-radius:6px;
cursor:pointer;
}

.menu-item:hover {
background-color:#f0f2f6;
}

.active {
background-color:#ff4b4b;
color:white;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)


st.set_page_config(
    page_title="롯데 AI 야구 플랫폼",
    layout="wide"
)

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼 ULTIMATE")


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
        return pd.read_csv("data/schedule.csv")
    except:
        return pd.DataFrame(columns=["date","opponent"])


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
        return pd.DataFrame(columns=["team","win","lose"])



news = load_news()
players = load_players()
schedule = load_schedule()
games = load_games()
standings = load_standings()


# 사이드바
menu = st.sidebar.selectbox(
"메뉴 선택",
[
"대시보드",
"뉴스",
"선수 분석",
"경기 일정",
"경기 결과",
"AI 분석",
"경기 시뮬레이터"
]
)


# =========================
# 대시보드
# =========================

if menu == "대시보드":

    st.header("📊 롯데 대시보드")

    col1,col2,col3 = st.columns(3)

    if len(games)>0:

        last10 = games.tail(10)

        wins = len(last10[last10["result"]=="W"])
        loses = len(last10[last10["result"]=="L"])

    else:

        wins=0
        loses=0


    elo = calculate_elo(wins,loses)

    with col1:
        st.metric("최근10경기 승",wins)

    with col2:
        st.metric("최근10경기 패",loses)

    with col3:
        st.metric("ELO 전력지수",elo)


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
# 선수 분석
# =========================

if menu == "선수 분석":

    st.header("🏏 선수 OPS")

    st.dataframe(players)

    if len(players)>0:

        fig,ax = plt.subplots()

        ax.bar(players["name"],players["ops"])

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

if menu == "AI 분석":

    st.header("🤖 AI 경기 분석")

    prob = predict_win_probability()

    st.metric("AI 승률 예측",prob)


    st.subheader("시즌 승률 그래프")

    if len(games)>0:

        games["win"]=games["result"].apply(lambda x:1 if x=="W" else 0)

        games["cum"]=games["win"].cumsum()

        games["game"]=range(1,len(games)+1)

        fig,ax=plt.subplots()

        ax.plot(games["game"],games["cum"])

        st.pyplot(fig)



# =========================
# 경기 시뮬레이터
# =========================

if menu == "경기 시뮬레이터":

    st.header("🎮 경기 시뮬레이터")

    if st.button("경기 시뮬레이션 실행"):

        lotte,opp,result = simulate_game()

        st.write("롯데:",lotte)

        st.write("상대:",opp)

        st.subheader(result)
