import streamlit as st
import pandas as pd
from players import players

st.set_page_config(layout="wide")

st.title("⚾ 롯데 자이언츠 팬 대시보드")

tabs = st.tabs(["오늘 경기","뉴스","선수 뉴스","KBO 순위","영상"])


# -------------------
# 오늘 경기
# -------------------
with tabs[0]:

    st.header("⚾ 오늘 경기 결과")

    try:

        df=pd.read_csv("result.csv")

        today=df[df["match"].str.contains("롯데")]

        if len(today)==0:

            st.write("오늘 롯데 경기 없음")

        else:

            for _,r in today.iterrows():

                st.subheader(r["match"])
                st.write("스코어:",r["score"])

    except:

        st.write("경기 결과 데이터 없음")


# -------------------
# 뉴스
# -------------------

with tabs[1]:

    st.header("📰 롯데 뉴스")

    df=pd.read_csv("news.csv")

    df["date"]=pd.to_datetime(df["date"])

    date=st.date_input("날짜 선택")

    f=df[df["date"]==pd.to_datetime(date)]

    st.write("기사:",len(f))

    for _,r in f.iterrows():

        st.subheader(r["title"])
        st.link_button("기사보기",r["link"])
        st.divider()


# -------------------
# 선수 뉴스
# -------------------
with tabs[2]:

    st.header("⚾ 롯데 선수 뉴스")

    df=pd.read_csv("news.csv")

    for p in players:

        st.subheader(p)

        result=df[df["title"].str.contains(p,na=False)]

        if len(result)==0:

            st.write("관련 뉴스 없음")

        else:

            for _,r in result.iterrows():

                st.write(r["title"])
                st.link_button("기사보기",r["link"])

# -------------------
# 순위
# -------------------

with tabs[3]:

    st.header("📊 KBO 순위")

    rank=pd.read_csv("rank.csv")

    st.dataframe(rank)

# -------------------
# 영상
# -------------------

with tabs[4]:

    st.header("📺 롯데 자이언츠 영상")

    st.video("https://www.youtube.com/watch?v=6z6L1v3c8a8")