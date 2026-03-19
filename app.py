
import streamlit as st
import pandas as pd

st.title("롯데 AI 플랫폼 (안정판)")

def load(name):
    try:
        return pd.read_csv(f"data/{name}")
    except:
        return pd.DataFrame()

menu = st.sidebar.selectbox("메뉴", ["OPS","투수","일정"])

if menu == "OPS":
    df = load("players_stats.csv")
    st.dataframe(df)

elif menu == "투수":
    df = load("pitcher_stats.csv")
    st.dataframe(df)

elif menu == "일정":
    df = load("schedule.csv")
    st.dataframe(df)
