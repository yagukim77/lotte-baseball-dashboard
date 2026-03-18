import pandas as pd

BASE_ELO = 1500
K_FACTOR = 24
HOME_ADVANTAGE = 18


def expected(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))


def _safe_float(x, default=0):
    try:
        return float(x)
    except Exception:
        return default


def calculate_team_elo():
    try:
        df = pd.read_csv("data/games.csv").copy()
    except Exception:
        return pd.DataFrame(columns=["team", "elo"])

    required = {"home", "away", "runs", "allowed"}
    if df.empty or not required.issubset(df.columns):
        return pd.DataFrame(columns=["team", "elo"])

    teams = sorted(set(df["home"].dropna().tolist() + df["away"].dropna().tolist()))
    elo = {team: BASE_ELO for team in teams}

    for _, row in df.iterrows():
        home = str(row["home"]).strip()
        away = str(row["away"]).strip()

        if home not in elo:
            elo[home] = BASE_ELO
        if away not in elo:
            elo[away] = BASE_ELO

        home_runs = _safe_float(row["runs"], 0)
        away_runs = _safe_float(row["allowed"], 0)

        home_pre = elo[home] + HOME_ADVANTAGE
        away_pre = elo[away]

        home_exp = expected(home_pre, away_pre)
        away_exp = expected(away_pre, home_pre)

        if home_runs > away_runs:
            home_score = 1
            away_score = 0
        elif home_runs < away_runs:
            home_score = 0
            away_score = 1
        else:
            home_score = 0.5
            away_score = 0.5

        margin = abs(home_runs - away_runs)
        margin_bonus = 1 + min(margin * 0.08, 0.4)

        elo[home] = round(elo[home] + K_FACTOR * margin_bonus * (home_score - home_exp), 2)
        elo[away] = round(elo[away] + K_FACTOR * margin_bonus * (away_score - away_exp), 2)

    return pd.DataFrame({
        "team": list(elo.keys()),
        "elo": list(elo.values())
    }).sort_values("elo", ascending=False).reset_index(drop=True)


def get_team_elo(team_name: str) -> float:
    df = calculate_team_elo()
    target = df[df["team"] == team_name]
    if target.empty:
        return BASE_ELO
    return float(target.iloc[0]["elo"])
