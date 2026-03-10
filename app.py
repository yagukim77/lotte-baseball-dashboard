import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("data/news.csv"):
    df = pd.DataFrame(columns=["date","title","link"])
    df.to_csv("data/news.csv",index=False)

if not os.path.exists("data/articles.csv"):
    df = pd.DataFrame(columns=["title","text"])
    df.to_csv("data/articles.csv",index=False)
    
import subprocess
subprocess.run(["python","crawler_news.py"])
subprocess.run(["python","crawler_article.py"])

from ai_summary import summarize
from analysis import extract_keywords, predict_win
from wordcloud_gen import make_cloud

st.set_page_config(
page_title="롯데 AI 야구 대시보드",
layout="wide"
)

st.title("⚾ LOTTE GIANTS AI DASHBOARD")

tabs = st.tabs([
"오늘 경기",
"실시간 스코어",
"뉴스",
"AI 요약",
"키워드 분석",
"워드 클라우드",
"선수 기록",
"승율 예측",
"영상"
])

# 오늘 경기
with tabs[0]:

    st.header("오늘 롯데 경기")

    try:

        schedule=pd.read_csv("data/schedule.csv")

        lotte=schedule[schedule["match"].str.contains("롯데")]

    if len(lotte)>0:

        st.warning("⚾ 오늘 롯데 경기 있습니다!")

        st.dataframe(lotte)

    except:

        st.write("경기 없음")

#실시간 스코어
with tabs[1]:

    st.header("⚾ 실시간 경기")

    try:

        df = pd.read_csv("score.csv")

        lotte = df[df["match"].str.contains("롯데")]

        if len(lotte)==0:

            st.write("오늘 경기 없음")

        else:

            for _,r in lotte.iterrows():

                st.subheader(r["match"])
                st.write("스코어:", r["score"])

    except:

        st.write("스코어 데이터 없음")


# 뉴스
with tabs[2]:

    st.header("AI 뉴스 요약")

    articles = pd.read_csv("data/articles.csv")

    for _,r in articles.head(5).iterrows():

        summary = summarize(r["text"])

        st.subheader(r["title"])

        st.write(summary)

    except:

        st.write("뉴스 없음")

# AI 요약
with tabs[3]:

    st.header("AI 뉴스 요약")

    df = pd.read_csv("news.csv")

    for _,r in df.head(5).iterrows():

        summary = summarize(r["title"])

        st.subheader(r["title"])

        st.write(summary)

        st.link_button("기사보기", r["link"])

    except:

        st.write("요약 데이터 없음")


# 키워드 분석
with tabs[4]:

    st.header("뉴스 키워드 분석")

    articles = pd.read_csv("data/articles.csv")

    keywords = extract_keywords(articles["text"])

    words = [k[0] for k in keywords]
    counts = [k[1] for k in keywords]

    fig, ax = plt.subplots()

    ax.bar(words, counts)

    st.pyplot(fig)


# 워드클라우드

with tabs[5]:

    st.header("뉴스 워드클라우드")

    articles = pd.read_csv("data/articles.csv")

    keywords = extract_keywords(articles["text"])

    words = []

    for w,c in keywords:

        words += [w]*c

    fig = make_cloud(words)

    st.pyplot(fig)

# 선수 기록
with tabs[6]:

    st.header("롯데 선수 기록")

    try:

        players=pd.read_csv("players_stats.csv")

        fig,ax=plt.subplots()

        ax.bar(players["player"],players["ops"])

        ax.set_title("롯데 OPS 분석")

        st.pyplot(fig)

    except:

        st.write("선수 데이터 없음")

# 롯데 승율 예측
with tabs[7]:

    st.header("AI 승률 예측")

    win = predict_win()

    st.metric("오늘 승리 확률", f"{win*100}%")

# 영상
with tabs[8]:

    st.header("롯데 하이라이트")

    yt=pd.read_csv("data/youtube.csv")

    for _,v in yt.head(5).iterrows():

    st.subheader(v["title"])

    st.video(v["link"])
    )








