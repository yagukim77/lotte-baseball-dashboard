import streamlit as st
import pandas as pd

st.title("⚔️ 팀 전력 비교")

df = pd.read_csv("data/kbo_hitters.csv")

teams = df["team"].unique()

teamA = st.selectbox("팀A", teams)
teamB = st.selectbox("팀B", teams)

opsA = df[df["team"] == teamA]["ops"].astype(float).mean()
opsB = df[df["team"] == teamB]["ops"].astype(float).mean()

st.write(teamA, "평균 OPS", round(opsA,3))
st.write(teamB, "평균 OPS", round(opsB,3))

st.bar_chart({
    teamA: opsA,
    teamB: opsB
})
