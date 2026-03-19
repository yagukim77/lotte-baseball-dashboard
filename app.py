import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="롯데 AI 플랫폼 안정판", layout="wide")
st.title("⚾ 롯데 AI 플랫폼 안정판")

@st.cache_data(ttl=600)
def load_csv(name):
    path = os.path.join("data", name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def show_df(df):
    st.dataframe(df, use_container_width=True, hide_index=True)

menu = st.sidebar.selectbox("메뉴", ["OPS", "투수", "일정", "최근 경기", "팀 스탯", "상태 점검"])

players = load_csv("players_stats.csv")
pitchers = load_csv("pitcher_stats.csv")
schedule = load_csv("schedule.csv")
games = load_csv("games.csv")
team_stats = load_csv("team_stats.csv")

if menu == "OPS":
    st.header("타자 기록")
    if players.empty:
        st.info("players_stats.csv 데이터가 없습니다.")
    else:
        show_df(players)
        if {"player", "ops"}.issubset(players.columns):
            top = players.sort_values("ops", ascending=False).head(20)
            fig = px.bar(top, x="player", y="ops", color="team" if "team" in top.columns else None, title="OPS TOP 20")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "투수":
    st.header("투수 기록")
    if pitchers.empty:
        st.info("pitcher_stats.csv 데이터가 없습니다.")
    else:
        show_df(pitchers)
        if {"player", "era"}.issubset(pitchers.columns):
            top = pitchers.sort_values("era", ascending=True).head(20)
            fig = px.bar(top, x="player", y="era", color="team" if "team" in top.columns else None, title="ERA TOP 20")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "일정":
    st.header("경기 일정")
    if schedule.empty:
        st.info("schedule.csv 데이터가 없습니다.")
    else:
        show_df(schedule)

elif menu == "최근 경기":
    st.header("최근 경기")
    if games.empty:
        st.info("games.csv 데이터가 없습니다. 종료 경기 데이터가 아직 없을 수 있습니다.")
    else:
        show_df(games)
        if "result" in games.columns:
            lotte_home = games[games["home"] == "롯데"]
            if not lotte_home.empty:
                recent = lotte_home.tail(10)
                wins = (recent["result"] == "W").sum()
                losses = (recent["result"] == "L").sum()
                c1, c2 = st.columns(2)
                c1.metric("최근 10경기 승", int(wins))
                c2.metric("최근 10경기 패", int(losses))

elif menu == "팀 스탯":
    st.header("팀 스탯")
    if team_stats.empty:
        st.info("team_stats.csv 데이터가 없습니다.")
    else:
        show_df(team_stats)
        if {"team", "team_ops"}.issubset(team_stats.columns):
            fig = px.bar(team_stats.sort_values("team_ops", ascending=False), x="team", y="team_ops", title="팀 OPS")
            st.plotly_chart(fig, use_container_width=True)
        if {"team", "era"}.issubset(team_stats.columns):
            fig = px.bar(team_stats.sort_values("era", ascending=True), x="team", y="era", title="팀 ERA")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.header("상태 점검")
    checks = []
    for name, df in [
        ("players_stats.csv", players),
        ("pitcher_stats.csv", pitchers),
        ("schedule.csv", schedule),
        ("games.csv", games),
        ("team_stats.csv", team_stats),
    ]:
        checks.append({
            "file": name,
            "rows": len(df),
            "status": "OK" if len(df) > 0 else "WARNING",
        })
    check_df = pd.DataFrame(checks)
    show_df(check_df)
