import streamlit as st
import pandas as pd
from datetime import datetime

from ai.score_predictor import predict_score
from ai.simulator import simulate_game
from ai.lineup_optimizer import recommend_lineup

from analysis.keywords import extract_keywords
from analysis.war_analysis import calculate_war
from analysis.team_matchup import team_record
from analysis.recent_games import recent_10
from analysis.season import season_winrate

from crawlers.live_score import get_live_score
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="롯데 AI 야구 플랫폼",page_icon="⚾",layout="wide")

st.title("⚾ 롯데 AI 야구 플랫폼")

menu = st.sidebar.selectbox("메뉴",
[
"홈",
"뉴스",
"뉴스 키워드 분석",
"경기 일정",
"실시간 경기",
"선수 OPS 분석",
"선수 WAR 분석",
"AI 라인업 추천",
"AI 승률 예측",
"AI 예상 스코어",
"경기 시뮬레이터",
"팀별 승률 분석",
"최근 10경기",
"시즌 승률 그래프"
])

# 홈
if menu=="홈":

    schedule=pd.read_csv("data/schedule.csv")

    today=datetime.today().strftime("%Y-%m-%d")

    game=schedule[schedule["date"]==today]

    if len(game)>0:

        opponent=game.iloc[0]["opponent"]

        st.warning(f"⚾ 오늘 경기 : 롯데 vs {opponent}")

    else:

        st.info("오늘 경기 없음")


# 뉴스
if menu=="뉴스":

    news=pd.read_csv("data/news.csv")

    for i,row in news.head(20).iterrows():

        st.subheader(row["title"])
        st.write(row["summary"])
        st.markdown(row["link"])
        st.divider()


# 뉴스 키워드
if menu=="뉴스 키워드 분석":

    news=pd.read_csv("data/news.csv")

    keywords=extract_keywords(news["title"])

    st.write(keywords)


# 경기 일정
if menu=="경기 일정":

    schedule=pd.read_csv("data/schedule.csv")

    st.dataframe(schedule)


# 실시간 경기
if menu=="실시간 경기":

    st_autorefresh(interval=30000)

    score=get_live_score()

    st.success(score)


# OPS
if menu=="선수 OPS 분석":

    players=pd.read_csv("data/players_stats.csv")

    st.dataframe(players)

    top=players.sort_values("ops",ascending=False).head(10)

    st.bar_chart(top.set_index("name")["ops"])


# WAR
if menu=="선수 WAR 분석":

    players=pd.read_csv("data/players_stats.csv")

    players=calculate_war(players)

    st.dataframe(players)


# 라인업
if menu=="AI 라인업 추천":

    players=pd.read_csv("data/players_stats.csv")

    lineup=recommend_lineup(players)

    for i,p in enumerate(lineup):

        st.write(i+1,p)


# 승률 예측
if menu=="AI 승률 예측":

    ops=st.slider("롯데 OPS",0.6,0.9,0.72)

    opp=st.slider("상대 OPS",0.6,0.9,0.68)

    prob=0.5+(ops-opp)

    st.metric("승률",f"{int(prob*100)}%")


# 예상 스코어
if menu=="AI 예상 스코어":

    t=st.slider("롯데 득점",3.0,7.0,4.8)

    o=st.slider("상대 득점",3.0,7.0,4.3)

    score=predict_score(t,o)

    st.metric("예상 스코어",f"{score[0]} : {score[1]}")


# 시뮬레이터
if menu=="경기 시뮬레이터":

    t=st.slider("롯데 공격력",3.0,7.0,4.8)

    o=st.slider("상대 공격력",3.0,7.0,4.3)

    result=simulate_game(t,o)

    st.metric("승률",f"{int(result*100)}%")


# 팀별 승률
if menu=="팀별 승률 분석":

    df=pd.read_csv("data/games.csv")

    result=team_record(df)

    st.dataframe(result)


# 최근 경기
if menu=="최근 10경기":

    df=pd.read_csv("data/games.csv")

    result=recent_10(df)

    st.dataframe(result)


# 시즌 그래프
if menu=="시즌 승률 그래프":

    df=season_winrate()

    st.line_chart(df["win_rate"])