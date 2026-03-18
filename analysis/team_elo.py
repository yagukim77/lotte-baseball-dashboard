import pandas as pd

BASE_ELO = 1500
K_FACTOR = 20

def expected(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))

def calculate_team_elo():
    try:
        df = pd.read_csv("data/games.csv").copy()
    except Exception:
        return pd.DataFrame(columns=["team", "elo"])

    if df.empty:
        return pd.DataFrame(columns=["team", "elo"])

    required = {"home", "away", "runs", "allowed", "result"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["team", "elo"])

    teams = sorted(set(df["home"].dropna().tolist() + df["away"].dropna().tolist()))
    elo = {team: BASE_ELO for team in teams}

    for _, row in df.iterrows():
        home = row["home"]
        away = row["away"]

        if home not in elo:
            elo[home] = BASE_ELO
        if away not in elo:
            elo[away] = BASE_ELO

        home_elo = elo[home]
        away_elo = elo[away]

        home_exp = expected(home_elo, away_elo)
        away_exp = expected(away_elo, home_elo)

        home_runs = float(row["runs"]) if pd.notna(row["runs"]) else 0
        away_runs = float(row["allowed"]) if pd.notna(row["allowed"]) else 0

        if home_runs > away_runs:
            home_score = 1
            away_score = 0
        elif home_runs < away_runs:
            home_score = 0
            away_score = 1
        else:
            home_score = 0.5
            away_score = 0.5

        elo[home] = round(home_elo + K_FACTOR * (home_score - home_exp), 2)
        elo[away] = round(away_elo + K_FACTOR * (away_score - away_exp), 2)

    out = pd.DataFrame({
        "team": list(elo.keys()),
        "elo": list(elo.values())
    }).sort_values("elo", ascending=False)

    return out

def get_team_elo(team_name: str) -> float:
    elo_df = calculate_team_elo()
    target = elo_df[elo_df["team"] == team_name]
    if target.empty:
        return BASE_ELO
    return float(target.iloc[0]["elo"])
