import os
import pandas as pd

try:
    import streamlit as st
except Exception:
    st = None


def _read_csv(path: str):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def render_recent_and_live():
    schedule = _read_csv("data/schedule.csv")
    games = _read_csv("data/games.csv")
    live = _read_csv("data/live_score.csv")

    if st is None:
        print("streamlit not installed")
        print("schedule rows:", len(schedule))
        print("games rows:", len(games))
        print("live rows:", len(live))
        return

    st.title("롯데 AI 야구 플랫폼")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("최근 종료 경기")
        if games.empty:
            st.info("games.csv 없음 또는 종료 경기 없음")
        else:
            show = games.copy()
            for c in ["away_score", "home_score"]:
                if c in show.columns:
                    show[c] = show[c].fillna("")
            st.dataframe(show.sort_values(by=["date", "time"], ascending=False), use_container_width=True)

    with col2:
        st.subheader("실시간 / 경기전 / 취소")
        if live.empty:
            st.info("live_score.csv 없음")
        else:
            show = live.copy()
            order = pd.CategoricalDtype(
                categories=["진행중", "경기전", "우천취소", "취소", "중단", "서스펜디드", "종료"],
                ordered=True,
            )
            if "status" in show.columns:
                show["status_order"] = show["status"].astype(str).astype(order)
                show = show.sort_values(by=["status_order", "date", "time"], ascending=[True, False, True]).drop(columns=["status_order"])
            st.dataframe(show, use_container_width=True)

    st.subheader("통합 일정")
    if schedule.empty:
        st.info("schedule.csv 없음")
    else:
        st.dataframe(schedule, use_container_width=True)


if __name__ == "__main__":
    render_recent_and_live()
