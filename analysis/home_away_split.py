import pandas as pd


def get_home_away_split_factor(team_name: str, is_home: bool):
    try:
        df = pd.read_csv("data/games.csv").copy()
    except Exception:
        return 1.0

    if df.empty or not {"home", "away", "runs", "allowed"}.issubset(df.columns):
        return 1.0

    if is_home:
        games = df[df["home"] == team_name].tail(20)
        if games.empty:
            return 1.0
        avg_runs = games["runs"].astype(float).mean()
    else:
        games = df[df["away"] == team_name].tail(20)
        if games.empty:
            return 1.0
        avg_runs = games["allowed"].astype(float).mean()

    # 4.5를 기준 중립값으로 사용
    factor = avg_runs / 4.5 if avg_runs > 0 else 1.0
    return round(min(max(factor, 0.85), 1.15), 3)
