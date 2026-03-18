import streamlit as st
import pandas as pd
import plotly.express as px

st.title("KBO 팀 전력 분석")

df=pd.read_csv("data/team_stats.csv")

st.dataframe(df)

fig=px.bar(
    df,
    x="team",
    y="team_ops",
    height=400
)

st.plotly_chart(fig)

top=df.sort_values("team_ops",ascending=False)

st.subheader("공격력 순위")

st.dataframe(top)
