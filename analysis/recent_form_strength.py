import pandas as pd
from analysis.team_elo import get_team_elo


def get_recent_form_strength(team_name: str, n=10):
    try:
        df = pd.read_csv("data/games.csv").copy()
    except Exception:
        return {
            "win_rate": 0.5,
            "avg_runs": 4.5,
            "avg_allowed": 4.5,
            "strength_score": 0.5
        }

    if df.empty:
        return {
            "win_rate": 0.5,
            "avg_runs": 4.5,
            "avg_allowed": 4.5,
            "strength_score": 0.5
        }

    if not {"home", "away", "runs", "allowed"}.issubset(df.columns):
        return {
            "win_rate": 0.5,
            "avg_runs": 4.5,
            "avg_allowed": 4.5,
            "strength_score": 0.5
        }

    team_games = df[(df["home"] == team_name) | (df["away"] == team_name)].tail(n)

    if team_games.empty:
        return {
            "win_rate": 0.5,
            "avg_runs": 4.5,
            "avg_allowed": 4.5,
            "strength_score": 0.5
        }

    wins = 0
    scores = []
    alloweds = []
    opp_elo_scores = []

    for _, row in team_games.iterrows():
        home = row["home"]
        away = row["away"]
        home_runs = float(row["runs"])
        away_runs = float(row["allowed"])

        is_home = home == team_name
        opp = away if is_home else home

        my_runs = home_runs if is_home else away_runs
        opp_runs = away_runs if is_home else home_runs

        if my_runs > opp_runs:
            wins += 1

        scores.append(my_runs)
        alloweds.append(opp_runs)
        opp_elo_scores.append(get_team_elo(opp))

    win_rate = wins / len(team_games)
    avg_runs = sum(scores) / len(scores)
    avg_allowed = sum(alloweds) / len(alloweds)
    avg_opp_elo = sum(opp_elo_scores) / len(opp_elo_scores)

    # 상대 강도 반영: 평균 상대 ELO가 높을수록 폼 점수 가산
    strength_score = (
        0.45 * win_rate
        + 0.20 * min(avg_runs / 7, 1)
        + 0.15 * max(0, 1 - avg_allowed / 7)
        + 0.20 * min(avg_opp_elo / 1700, 1)
    )

    return {
        "win_rate": round(win_rate, 3),
        "avg_runs": round(avg_runs, 2),
        "avg_allowed": round(avg_allowed, 2),
        "strength_score": round(strength_score, 3)
    }
