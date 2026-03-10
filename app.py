import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from ai_summary import summarize

st.set_page_config(page_title="Lotte Baseball Dashboard")

st.title("⚾ LOTTE GIANTS DASHBOARD")

tabs = st.tabs([
"오늘 경기",
"뉴스",
"AI 뉴스 요약",
"선수 뉴스",
"선수 기록",
"분석",
"영상"
])

# 오늘 경기
with tabs[0]:

    st.header("오늘 롯데 경기")

    try:

        df = pd.read_csv("schedule.csv")

        lotte = df[df["match"].str.contains("롯데")]

        for _,r in lotte.iterrows():

            st.subheader(r["match"])
            st.write(r["stadium"])

    except:

        st.write("경기 없음")

# 뉴스
with tabs[1]:

    st.header("롯데 뉴스")

    df = pd.read_csv("news.csv")

    for _,r in df.head(10).iterrows():

        st.subheader(r["title"])

        st.link_button("기사보기", r["link"])

    except:

        st.write("뉴스 없음")

# AI 요약
with tabs[2]:

    st.header("AI 뉴스 요약")

    df = pd.read_csv("news.csv")

    for _,r in df.head(5).iterrows():

        summary = summarize(r["title"])

        st.subheader(r["title"])

        st.write(summary)

    except:

        st.write("요약 데이터 없음")

# 선수 뉴스
players = [
"한동희",
"윤동희",
"김원중",
"엘빈 로드리게스",
"제레미 비슬리"
    
]

with tabs[3]:

    df = pd.read_csv("news.csv")

    for p in players:

        st.subheader(p)

        result = df[df["title"].str.contains(p, na=False)]

        for _,r in result.iterrows():

            st.write(r["title"])
            st.link_button("기사", r["link"])


# 선수 기록
with tabs[4]:

    st.header("선수 기록")

    df = pd.read_csv("players_stats.csv")

    st.dataframe(df)

    except:

        st.write("선수 기록 없음")

# 롯데 분석
with tabs[5]:

    st.header("📊 롯데 승률 그래프")

    games = [10,20,30,40,50]
    winrate = [0.4,0.45,0.48,0.52,0.55]

    fig, ax = plt.subplots()

    ax.plot(games, winrate)

    ax.set_xlabel("Games")
    ax.set_ylabel("Win Rate")

    st.pyplot(fig)

# 영상
with tabs[6]:

    st.header("롯데 하이라이트")

    st.link_button(
    "유튜브 하이라이트",
    "https://www.youtube.com/results?search_query=롯데+자이언츠+하이라이트"
    )



