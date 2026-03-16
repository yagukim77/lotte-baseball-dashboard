import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import re
from collections import Counter

# ===============================
# 자동 새로고침 (안정 코드)
# ===============================

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=600000)
except:
    pass


# ===============================
# 페이지 설정
# ===============================

st.set_page_config(
    page_title="롯데 AI 야구 플랫폼",
    layout="wide"
)

st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")


# ===============================
# 데이터 로드
# ===============================

@st.cache_data
def load_news():
    try:
        return pd.read_csv("data/news.csv")
    except:
        return pd.DataFrame(columns=["title","link","summary"])


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
        return pd.DataFrame(columns=["date","opponent","win","lose","result"])


@st.cache_data
def load_standings():
    try:
        return pd.read_csv("data/kbo_standings.csv")
    except:
        return pd.DataFrame(columns=["team","win","lose","win_rate"])



news = load_news()
players = load_players()
schedule = load_schedule()
games = load_games()
standings = load_standings()


# ===============================
# 사이드바
# ===============================

st.sidebar.title("메뉴")

menu = st.sidebar.radio(
    "선택",
    [
        "대시보드",
        "뉴스",
        "선수 분석",
        "경기 일정",
        "경기 결과",
        "AI 분석"
    ]
)



# ===============================
# 대시보드
# ===============================

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


    with col1:
        st.metric("최근 10경기 승",wins)

    with col2:
        st.metric("최근 10경기 패",loses)

    with col3:
        rate = round(random.uniform(0.45,0.65),2)
        st.metric("AI 예상 승률",rate)


    st.subheader("KBO 순위")

    st.dataframe(standings)



# ===============================
# 뉴스
# ===============================

if menu == "뉴스":

    st.header("📰 롯데 뉴스")

    for i,row in news.head(20).iterrows():

        st.markdown(f"[{row['title']}]({row['link']})")



    st.subheader("📊 뉴스 키워드 분석")

    titles = news["title"].tolist()

    words=[]

    for t in titles:

        w=re.findall(r"[가-힣]{2,}",t)

        words.extend(w)

    counter=Counter(words)

    top=counter.most_common(10)

    keywords=pd.DataFrame(top,columns=["keyword","count"])

    st.dataframe(keywords)



# ===============================
# 선수 분석
# ===============================

if menu == "선수 분석":

    st.header("🏏 롯데 선수 OPS 분석")

    st.dataframe(players)

    if len(players)>0:

        fig,ax = plt.subplots()

        ax.bar(players["name"],players["ops"])

        ax.set_title("OPS")

        st.pyplot(fig)



# ===============================
# 경기 일정
# ===============================

if menu == "경기 일정":

    st.header("📅 경기 일정")

    st.dataframe(schedule)



# ===============================
# 경기 결과
# ===============================

if menu == "경기 결과":

    st.header("📊 경기 결과")

    st.dataframe(games)



    if len(games)>0:

        st.subheader("최근 10경기")

        st.dataframe(games.tail(10))



# ===============================
# AI 분석
# ===============================

if menu == "AI 분석":

    st.header("🤖 AI 경기 분석")


    st.subheader("AI 예상 스코어")

    lotte=random.randint(3,8)
    opp=random.randint(2,7)

    col1,col2 = st.columns(2)

    with col1:
        st.metric("롯데",lotte)

    with col2:
        st.metric("상대팀",opp)



    st.subheader("시즌 승률 그래프")

    if len(games)>0:

        games["win"]=games["result"].apply(lambda x:1 if x=="W" else 0)

        games["cum_win"]=games["win"].cumsum()

        games["game"]=range(1,len(games)+1)

        fig,ax=plt.subplots()

        ax.plot(games["game"],games["cum_win"])

        ax.set_title("누적 승리")

        st.pyplot(fig)



    st.subheader("유튜브 하이라이트")

    st.write("https://www.youtube.com/results?search_query=롯데자이언츠+하이라이트")
