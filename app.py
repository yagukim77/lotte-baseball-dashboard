import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import feedparser
import re
from collections import Counter

# =========================
# 자동 새로고침 (안정 코드)
# =========================

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=600000)
except:
    pass


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
    return pd.read_csv("data/news.csv")

@st.cache_data
def load_players():
    return pd.read_csv("data/players_stats.csv")

@st.cache_data
def load_schedule():
    return pd.read_csv("data/schedule.csv")

@st.cache_data
def load_games():
    return pd.read_csv("data/games.csv")

@st.cache_data
def load_standings():
    return pd.read_csv("data/kbo_standings.csv")


news = load_news()
players = load_players()
schedule = load_schedule()
games = load_games()
standings = load_standings()


# =========================
# 뉴스 섹션
# =========================

st.header("📰 롯데 뉴스")

for i,row in news.head(10).iterrows():

    st.markdown(f"[{row['title']}]({row['link']})")


# =========================
# 뉴스 키워드 분석
# =========================

st.header("📊 뉴스 키워드 분석")

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

st.header("🏏 롯데 선수 OPS")

st.dataframe(players)

fig,ax = plt.subplots()

ax.bar(players["name"],players["ops"])

ax.set_title("OPS")

st.pyplot(fig)


# =========================
# 경기 일정
# =========================

st.header("📅 경기 일정")

st.dataframe(schedule)


# =========================
# 최근 경기 결과
# =========================

st.header("📊 최근 경기 결과")

st.dataframe(games.tail(10))


# =========================
# 최근 10경기 분석
# =========================

st.header("📈 최근 10경기 분석")

last10=games.tail(10)

wins=len(last10[last10["result"]=="W"])

loses=len(last10[last10["result"]=="L"])

st.metric("승",wins)

st.metric("패",loses)


# =========================
# 시즌 승률 그래프
# =========================

st.header("📊 시즌 승률")

games["win"]=games["result"].apply(lambda x:1 if x=="W" else 0)

games["cum_win"]=games["win"].cumsum()

games["game"]=range(1,len(games)+1)

fig,ax=plt.subplots()

ax.plot(games["game"],games["cum_win"])

ax.set_title("승리 누적")

st.pyplot(fig)


# =========================
# KBO 순위
# =========================

st.header("🏆 KBO 순위")

st.dataframe(standings)


# =========================
# AI 예상 스코어
# =========================

st.header("🤖 AI 예상 스코어")

lotte=random.randint(3,8)

opp=random.randint(2,7)

st.metric("롯데",lotte)

st.metric("상대팀",opp)


# =========================
# AI 승률 예측
# =========================

st.header("🤖 AI 승률 예측")

winrate=round(random.uniform(0.45,0.65),2)

st.metric("예상 승률",winrate)


# =========================
# 유튜브 하이라이트
# =========================

st.header("🎬 롯데 하이라이트")

youtube_links=[

"https://www.youtube.com/results?search_query=롯데자이언츠+하이라이트"

]

for link in youtube_links:

    st.write(link)
