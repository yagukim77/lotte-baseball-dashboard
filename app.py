import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="롯데 AI 플랫폼 안정판", layout="wide")
st.title("⚾ 롯데 AI 플랫폼 안정판")

def load_csv(name):
    path = os.path.join("data", name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

menu = st.sidebar.selectbox("메뉴", ["상태 점검", "타자", "투수", "일정", "최근 경기", "팀 스탯"])

files = {
    "players_stats.csv": load_csv("players_stats.csv"),
    "pitcher_stats.csv": load_csv("pitcher_stats.csv"),
    "schedule.csv": load_csv("schedule.csv"),
    "games.csv": load_csv("games.csv"),
    "team_stats.csv": load_csv("team_stats.csv"),
}

if menu == "상태 점검":
    rows = []
    for name, df in files.items():
        rows.append({"file": name, "rows": len(df), "exists": len(df) > 0})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
elif menu == "타자":
    st.dataframe(files["players_stats.csv"], use_container_width=True, hide_index=True)
elif menu == "투수":
    st.dataframe(files["pitcher_stats.csv"], use_container_width=True, hide_index=True)
elif menu == "일정":
    st.dataframe(files["schedule.csv"], use_container_width=True, hide_index=True)
elif menu == "최근 경기":
    st.dataframe(files["games.csv"], use_container_width=True, hide_index=True)
else:
    st.dataframe(files["team_stats.csv"], use_container_width=True, hide_index=True)
