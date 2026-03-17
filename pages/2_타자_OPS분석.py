import streamlit as st
import pandas as pd

st.title("🔥 KBO 타자 OPS 분석")

df = pd.read_csv("data/kbo_hitters.csv")

team = st.selectbox("팀 선택", df["team"].unique())

team_df = df[df["team"] == team]

st.dataframe(team_df)

st.subheader("OPS 그래프")

st.bar_chart(team_df.set_index("player")["ops"])
