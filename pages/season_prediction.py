import streamlit as st
from analysis.season_predictor import predict_season

st.title("AI 시즌 순위 예측")

df=predict_season()

st.dataframe(df)

lotte=df[df["team"]=="롯데"]

rank=int(lotte["pred_rank"])

st.metric(
    "롯데 예상 순위",
    rank
)
