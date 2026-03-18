import pandas as pd

BASE_ELO = 1500

def calculate_team_elo_table() -> pd.DataFrame:
    try:
        df = pd.read_csv("data/games.csv").copy()
    except Exception:
        return pd.DataFrame(columns=["team", "elo", "wins", "losses"])

    required = {"home", "away", "runs", "allowed"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["team", "elo", "wins", "losses"])

    teams = sorted(set(df["home"].dropna().astype(str)).union(set(df["away"].dropna().astype(str))))
    ratings = {team: BASE_ELO for team in teams}
    record = {team: {"wins": 0, "losses": 0} for team in teams}

    for _, row in df.iterrows():
        home = str(row["home"])
        away = str(row["away"])
        try:
            home_runs = float(row["runs"])
            away_runs = float(row["allowed"])
        except Exception:
            continue

        if home not in ratings or away not in ratings:
            continue
        if home_runs == away_runs:
            continue

        home_elo = ratings[home]
        away_elo = ratings[away]
        expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
        actual_home = 1.0 if home_runs > away_runs else 0.0
        k = 20

        ratings[home] = round(home_elo + k * (actual_home - expected_home), 2)
        ratings[away] = round(away_elo + k * ((1 - actual_home) - (1 - expected_home)), 2)

        if actual_home == 1.0:
            record[home]["wins"] += 1
            record[away]["losses"] += 1
        else:
            record[away]["wins"] += 1
            record[home]["losses"] += 1

    out = pd.DataFrame([
        {"team": team, "elo": ratings[team], "wins": record[team]["wins"], "losses": record[team]["losses"]}
        for team in teams
    ])
    return out.sort_values(["elo", "wins"], ascending=[False, False]).reset_index(drop=True)


def get_team_elo(team: str, default: float = BASE_ELO) -> float:
    table = calculate_team_elo_table()
    target = table[table["team"].astype(str) == str(team)]
    if target.empty:
        return default
    return float(target.iloc[0]["elo"])
