import streamlit as st
import pandas as pd
from analysis.game_simulator import simulate_game

st.title("⚾ 오늘 경기 AI 예측")

schedule = pd.read_csv("data/kbo_schedule.csv")

st.write("오늘 경기")

st.dataframe(schedule)

teamA = st.selectbox("홈팀", schedule["home"].unique())
teamB = st.selectbox("원정팀", schedule["away"].unique())

if st.button("AI 경기 시뮬레이션"):

    # 임시 공격력 (나중에 OPS 기반으로 바꿀 예정)
    teamA_attack = 4.8
    teamB_attack = 4.5

    result = simulate_game(teamA_attack, teamB_attack)

    st.subheader("AI 승률")

    st.write(teamA, round(result["teamA_win_rate"]*100,1), "%")
    st.write(teamB, round(result["teamB_win_rate"]*100,1), "%")

    st.subheader("예상 스코어")

    st.write(teamA, round(result["avg_scoreA"],1))
    st.write(teamB, round(result["avg_scoreB"],1))