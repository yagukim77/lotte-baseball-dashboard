import pandas as pd

DEFAULT_ERA = 4.50


def get_pitcher_era(name: str) -> float:
    if not name:
        return DEFAULT_ERA
    try:
        df = pd.read_csv("data/pitcher_stats.csv")
        target = df[df["player"].astype(str) == str(name)]
        if target.empty:
            return DEFAULT_ERA
        return float(target.iloc[0]["era"])
    except Exception:
        return DEFAULT_ERA


def starter_score(name: str) -> float:
    era = get_pitcher_era(name)
    return round(max(0.5, 6.5 - era), 2)


def adjust_attack_by_starter(team_attack: float, opp_starter_name: str) -> float:
    opp_pitch = starter_score(opp_starter_name)
    adjusted = team_attack - (opp_pitch - 2.0) * 0.18
    return round(max(2.0, adjusted), 2)
