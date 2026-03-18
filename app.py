import os
import streamlit as st
import pandas as pd
import plotly.express as px

from analysis.live_graph import build_live_win_history
from analysis.live_tuner import tune_live_win_prob
from analysis.probable_starter_matcher import get_probable_starters
from analysis.war_model import calculate_batter_war, calculate_team_war
from analysis.team_elo import calculate_team_elo, get_team_elo
from analysis.lineup_model import lineup_attack_score
from analysis.fan_features import short_game_comment, explain_prediction
from analysis.tuned_ai_model import build_tuned_prediction
from crawlers.live_score import get_lotte_live_game


st.set_page_config(page_title="롯데 AI 야구 플랫폼", layout="wide")


@st.cache_data(ttl=600)
def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        if os.path.getsize(path) == 0:
            return pd.DataFrame()
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def has_cols(df: pd.DataFrame, cols: list[str]) -> bool:
    return not df.empty and all(col in df.columns for col in cols)


def first_row(df: pd.DataFrame):
    if df.empty:
        return None
    return df.iloc[0]


def render_df(df: pd.DataFrame):
    st.dataframe(df, use_container_width=True, hide_index=True)


def normalize_status_text(status: str) -> str:
    text = str(status).strip()
    if "우천취소" in text:
        return "우천취소"
    if "우천중단" in text:
        return "우천중단"
    if "취소" in text:
        return "취소"
    if "경기전" in text or "예정" in text:
        return "경기전"
    if "종료" in text:
        return "경기종료"
    return text if text else "상태 미확인"


def live_reason_text(game: dict | None) -> str:
    if not game:
        return "현재 롯데 경기 정보가 없습니다."

    away = game.get("away", "")
    home = game.get("home", "")
    status = normalize_status_text(game.get("status", ""))

    if status == "우천취소":
        return f"오늘 롯데는 {away} vs {home} 경기였고, 현재 상태는 우천취소입니다."
    if status == "우천중단":
        return f"오늘 롯데는 {away} vs {home} 경기 중이며, 현재 우천중단 상태입니다."
    if status == "취소":
        return f"오늘 롯데는 {away} vs {home} 경기였고, 현재 취소 상태입니다."
    if status == "경기전":
        return f"오늘 롯데는 {away} vs {home} 경기 예정이며, 아직 시작 전입니다."
    if status == "경기종료":
        return f"오늘 롯데는 {away} vs {home} 경기이고, 현재 경기 종료 상태입니다."
    return f"오늘 롯데는 {away} vs {home} 경기이고, 현재 상태는 {status}입니다."


def season_prediction_notice(team_stats_df: pd.DataFrame) -> str:
    if team_stats_df.empty:
        return "아직 시즌 초반이거나 팀 기록 데이터가 부족해서 시즌 예측을 시작할 수 없습니다. 정규시즌 팀 기록이 누적되면 자동으로 예측이 표시됩니다."
    return ""


st.title("⚾ 롯데 자이언츠 AI 분석 플랫폼")
st.caption("튜닝 최종판 · 선발투수 fallback · 팀별 ELO · 상대강도 반영 · 홈/원정/구장/요일 반영")

menu = st.sidebar.selectbox(
    "메뉴",
    [
        "홈",
        "실시간 경기 AI",
        "오늘 경기 브리핑",
        "롯데 뉴스",
        "KBO 순위",
        "선수 OPS",
        "WAR 분석",
        "최근 경기",
        "경기 일정",
        "월간 일정",
        "팀 전력 비교",
        "팀 ELO",
        "라인업 AI",
        "시즌 예측",
    ],
)

schedule_df = load_csv("data/schedule.csv")
monthly_df = load_csv("data/monthly_schedule.csv")
standings_df = load_csv("data/kbo_standings.csv")
players_df = load_csv("data/players_stats.csv")
games_df = load_csv("data/games.csv")
team_stats_df = load_csv("data/team_stats.csv")


if menu == "홈":
    st.header("오늘 경기 AI 분석")

    if not has_cols(schedule_df, ["home", "away"]):
        st.info("오늘 경기 일정 데이터가 아직 준비되지 않았습니다. schedule.csv 컬럼(home, away, date, stadium, season_type)을 확인하세요.")
    else:
        today = first_row(schedule_df)
        home = str(today["home"]).strip()
        away = str(today["away"]).strip()
        season_type = str(today["season_type"]).strip() if "season_type" in schedule_df.columns else ""
        game_date = str(today["date"]).strip() if "date" in schedule_df.columns else ""
        stadium = str(today["stadium"]).strip() if "stadium" in schedule_df.columns else ""

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            game_date=game_date,
            stadium=stadium,
            home_starter=home_starter,
            away_starter=away_starter,
        )

        st.subheader(f"{away} vs {home} {season_type}")

        c1, c2 = st.columns(2)
        c1.metric(f"{away} 승률", f"{pred['away_prob']*100:.1f}%")
        c2.metric(f"{home} 승률", f"{pred['home_prob']*100:.1f}%")

        st.write(f"{away} 선발: {away_starter if away_starter else '팀 선발 평균치 적용'}")
        st.write(f"{home} 선발: {home_starter if home_starter else '팀 선발 평균치 적용'}")

        st.subheader("예상 스코어")
        st.write(f"{away} {pred['away_score']:.1f} : {home} {pred['home_score']:.1f}")

        x1, x2, x3, x4 = st.columns(4)
        x1.metric(f"{away} 공격력", pred["away_attack"])
        x2.metric(f"{home} 공격력", pred["home_attack"])
        x3.metric(f"{away} ELO", pred["away_elo"])
        x4.metric(f"{home} ELO", pred["home_elo"])

        y1, y2, y3, y4 = st.columns(4)
        y1.metric(f"{away} 최근폼", pred["away_form"]["strength_score"])
        y2.metric(f"{home} 최근폼", pred["home_form"]["strength_score"])
        y3.metric("구장 보정", pred["park_factor"])
        y4.metric("요일 보정", pred["weekday_factor"])

        st.info(
            explain_prediction(
                pred["home_prob"],
                pred["away_prob"],
                pred["home_attack"],
                pred["away_attack"],
                pred["home_elo"],
                pred["away_elo"],
            )
        )

elif menu == "실시간 경기 AI":
    st.header("🔥 실시간 경기 AI")

    game = get_lotte_live_game()
    st.info(live_reason_text(game))

    if game:
        away = game.get("away", "")
        home = game.get("home", "")
        away_score = int(game.get("away_score", 0))
        home_score = int(game.get("home_score", 0))
        status = normalize_status_text(game.get("status", ""))

        lotte_is_home = home == "롯데"
        lotte_score = home_score if lotte_is_home else away_score
        opp_score = away_score if lotte_is_home else home_score

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            home_starter=home_starter,
            away_starter=away_starter,
        )

        pre_prob = pred["home_prob"] if lotte_is_home else pred["away_prob"]

        live_prob = tune_live_win_prob(
            base_prob=pre_prob,
            lotte_score=lotte_score,
            opp_score=opp_score,
            status=status,
            is_home=lotte_is_home,
        )

        st.subheader(f"{away} vs {home}")
        st.write(f"현재 상태: {status}")
        st.write(f"스코어: {away} {away_score} : {home} {home_score}")

        c1, c2, c3 = st.columns(3)
        c1.metric("롯데 실시간 승률", f"{live_prob*100:.1f}%")
        c2.metric("프리게임 승률", f"{pre_prob*100:.1f}%")
        c3.metric("현재 점수차", lotte_score - opp_score)

        st.progress(float(live_prob))

        history_df = build_live_win_history(live_prob, status)
        fig = px.line(history_df, x="inning", y="win_prob", markers=True, title="이닝별 예상 승률 변화")
        st.plotly_chart(fig, use_container_width=True)

        st.info(short_game_comment(live_prob, status, lotte_score - opp_score))

elif menu == "오늘 경기 브리핑":
    st.header("📋 오늘 경기 브리핑")

    if not has_cols(schedule_df, ["home", "away"]):
        st.info("오늘 경기 브리핑용 일정 데이터가 없습니다.")
    else:
        today = first_row(schedule_df)
        home = str(today["home"]).strip()
        away = str(today["away"]).strip()
        game_date = str(today["date"]).strip() if "date" in schedule_df.columns else ""
        stadium = str(today["stadium"]).strip() if "stadium" in schedule_df.columns else ""

        away_starter, home_starter = get_probable_starters(home, away)

        pred = build_tuned_prediction(
            home_team=home,
            away_team=away,
            game_date=game_date,
            stadium=stadium,
            home_starter=home_starter,
            away_starter=away_starter,
        )

        st.subheader(f"{away} vs {home}")
        st.write(f"{away} 선발: {away_starter if away_starter else '팀 선발 평균치 적용'}")
        st.write(f"{home} 선발: {home_starter if home_starter else '팀 선발 평균치 적용'}")
        st.write(f"{away} 승률: {pred['away_prob']*100:.1f}%")
        st.write(f"{home} 승률: {pred['home_prob']*100:.1f}%")
        st.write(f"예상 스코어: {away} {pred['away_score']:.1f} : {home} {pred['home_score']:.1f}")

        a, b, c, d = st.columns(4)
        a.metric(f"{away} 최근폼", pred["away_form"]["strength_score"])
        b.metric(f"{home} 최근폼", pred["home_form"]["strength_score"])
        c.metric(f"{away} 선발 ERA", pred["away_starter_era"])
        d.metric(f"{home} 선발 ERA", pred["home_starter_era"])


elif menu == "뉴스 분석":
    st.header("롯데 뉴스")
    news_df = load_csv("data/news.csv")

    if news_df.empty:
        st.info("news.csv 데이터가 없습니다.")
    else:
        render_df(news_df)

        if "title" in news_df.columns:
            keyword_df = (
                news_df["title"]
                .astype(str)
                .str.extractall(r"([가-힣A-Za-z0-9]{2,})")[0]
                .value_counts()
                .head(15)
                .reset_index()
            )
            keyword_df.columns = ["keyword", "count"]

            if not keyword_df.empty:
                fig = px.bar(keyword_df, x="keyword", y="count", title="뉴스 키워드")
                st.plotly_chart(fig, use_container_width=True)


elif menu == "KBO 순위":
    st.header("KBO 순위")

    if standings_df.empty:
        st.info("kbo_standings.csv 데이터가 없습니다.")
    else:
        preferred = [
            "rank", "team", "games", "win", "lose", "draw", "win_rate", "gb",
            "avg", "era", "runs", "runs_allowed", "hr"
        ]
        cols = [c for c in preferred if c in standings_df.columns]
        if cols:
            render_df(standings_df[cols])
        else:
            render_df(standings_df)

        if {"team", "avg", "era"}.issubset(standings_df.columns):
            fig = px.bar(
                standings_df.sort_values("avg", ascending=False),
                x="team",
                y="avg",
                title="팀 타율"
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.bar(
                standings_df.sort_values("era", ascending=True),
                x="team",
                y="era",
                title="팀 평균자책점"
            )
            st.plotly_chart(fig2, use_container_width=True)

elif menu == "선수 OPS":
    st.header("🔥 KBO 타자 OPS 분석")

    if players_df.empty:
        st.info("players_stats.csv 데이터가 없습니다. 크롤러가 빈 파일을 만들었거나 시즌 구분/파싱이 실패한 상태입니다.")
    elif not has_cols(players_df, ["player", "team", "ops"]):
        st.info("players_stats.csv 컬럼이 맞지 않습니다. player, team, ops 컬럼이 필요합니다.")
    else:
        players_df["ops"] = pd.to_numeric(players_df["ops"], errors="coerce").fillna(0)
        render_df(players_df.sort_values("ops", ascending=False))

        top = players_df.sort_values("ops", ascending=False).head(20)
        fig = px.bar(top, x="player", y="ops", color="team", title="OPS TOP 20")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "WAR 분석":
    st.header("📊 WAR 분석")

    if players_df.empty:
        st.info("WAR 계산에 필요한 players_stats.csv가 비어 있습니다.")
    else:
        try:
            batter_war = calculate_batter_war()
            team_war = calculate_team_war()

            if batter_war.empty:
                st.info("WAR 계산용 타자 데이터가 부족합니다.")
            else:
                st.subheader("선수 WAR TOP 15")
                render_df(batter_war.head(15))
                fig1 = px.bar(batter_war.head(15), x="player", y="war", color="team")
                st.plotly_chart(fig1, use_container_width=True)

            if not team_war.empty:
                st.subheader("팀 WAR")
                render_df(team_war)
                fig2 = px.bar(team_war, x="team", y="war")
                st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.info(f"WAR 데이터 오류: {e}")

elif menu == "최근 경기":
    st.header("최근 경기")

    if games_df.empty:
        st.info("games.csv 데이터가 없습니다. 실제 경기 결과 크롤러를 먼저 안정화해야 합니다.")
    else:
        render_df(games_df.tail(10))

elif menu == "경기 일정":
    st.header("경기 일정")

    if schedule_df.empty:
        st.info("schedule.csv 데이터가 없습니다.")
    else:
        render_df(schedule_df)

elif menu == "월간 일정":
    st.header("월간 일정")

    if monthly_df.empty:
        st.info("monthly_schedule.csv 데이터가 없습니다. 월간 일정 크롤러가 아직 비어 있거나 저장에 실패한 상태입니다.")
    else:
        render_df(monthly_df)

        if {"home", "away"}.issubset(monthly_df.columns):
            lotte_df = monthly_df[(monthly_df["home"] == "롯데") | (monthly_df["away"] == "롯데")]
            st.subheader("롯데 일정")
            render_df(lotte_df)

elif menu == "팀 전력 비교":
    st.header("⚔️ 팀 전력 비교")

    if players_df.empty or "team" not in players_df.columns:
        st.info("팀 비교용 선수 데이터가 없습니다.")
    else:
        teams = sorted(players_df["team"].dropna().astype(str).unique())
        teamA = st.selectbox("팀A", teams)
        teamB = st.selectbox("팀B", teams)

        teamA_home = st.checkbox(f"{teamA} 홈 기준", value=True)
        teamB_home = st.checkbox(f"{teamB} 홈 기준", value=False)

        teamA_players = sorted(players_df[players_df["team"] == teamA]["player"].astype(str).unique())
        teamB_players = sorted(players_df[players_df["team"] == teamB]["player"].astype(str).unique())

        teamA_lineup = st.multiselect(f"{teamA} 라인업 수동 입력", teamA_players)
        teamB_lineup = st.multiselect(f"{teamB} 라인업 수동 입력", teamB_players)

        lineup_boost_a = lineup_attack_score(teamA_lineup, is_home=teamA_home) if teamA_lineup else None
        lineup_boost_b = lineup_attack_score(teamB_lineup, is_home=teamB_home) if teamB_lineup else None

        pred = build_tuned_prediction(
            home_team=teamA if teamA_home else teamB,
            away_team=teamB if teamA_home else teamA,
            lineup_boost_home=lineup_boost_a if teamA_home else lineup_boost_b,
            lineup_boost_away=lineup_boost_b if teamA_home else lineup_boost_a,
        )

        compare_df = pd.DataFrame({
            "team": [pred["away_team"], pred["home_team"]],
            "attack": [pred["away_attack"], pred["home_attack"]],
            "elo": [pred["away_elo"], pred["home_elo"]],
            "win_prob": [pred["away_prob"], pred["home_prob"]],
        })

        render_df(compare_df)

        fig = px.bar(compare_df, x="team", y="attack", title="공격력 비교")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric(f"{pred['away_team']} 승률", f"{pred['away_prob']*100:.1f}%")
        c2.metric(f"{pred['home_team']} 승률", f"{pred['home_prob']*100:.1f}%")

elif menu == "팀 ELO":
    st.header("📈 팀 ELO")

    try:
        elo_df = calculate_team_elo()
        if elo_df.empty:
            st.info("ELO 계산용 데이터가 없습니다. games.csv에 실제 경기 결과가 들어와야 합니다.")
        else:
            render_df(elo_df)
            fig = px.bar(elo_df, x="team", y="elo", title="팀별 ELO")
            st.plotly_chart(fig, use_container_width=True)
            st.metric("롯데 ELO", get_team_elo("롯데"))
    except Exception as e:
        st.info(f"ELO 계산 오류: {e}")

elif menu == "라인업 AI":
    st.header("🧠 라인업 AI")

    if players_df.empty or not has_cols(players_df, ["player", "team"]):
        st.info("라인업용 선수 데이터가 없습니다.")
    else:
        team = st.selectbox("팀 선택", sorted(players_df["team"].dropna().astype(str).unique()))
        is_home = st.checkbox("홈 경기 기준", value=True)
        player_list = sorted(players_df[players_df["team"] == team]["player"].astype(str).unique())

        default_players = player_list[:9] if len(player_list) >= 9 else player_list
        selected = st.multiselect("오늘 라인업 9명 선택", player_list, default=default_players)
        score = lineup_attack_score(selected, is_home=is_home)

        st.metric("라인업 공격력", score)

        if selected:
            selected_df = players_df[players_df["player"].isin(selected)]
            render_df(selected_df)

elif menu == "시즌 예측":
    st.header("시즌 예측")

    notice = season_prediction_notice(team_stats_df)
    if notice:
        st.info(notice)
    else:
        try:
            from analysis.season_predictor import predict_season
            df = predict_season()

            if df.empty:
                st.info("정규시즌 데이터가 더 쌓이면 시즌 예측이 시작됩니다.")
            else:
                render_df(df)
                lotte = df[df["team"] == "롯데"]
                if not lotte.empty and "pred_rank" in lotte.columns:
                    st.metric("롯데 예상 순위", int(lotte.iloc[0]["pred_rank"]))
        except Exception as e:
            st.info(f"시즌 예측 오류: {e}")
