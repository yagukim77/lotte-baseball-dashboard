import pandas as pd


def calculate_batter_war():
    df = pd.read_csv("data/players_stats.csv").copy()
    df["ops"] = pd.to_numeric(df["ops"], errors="coerce").fillna(0)
    df["hr"] = pd.to_numeric(df["hr"], errors="coerce").fillna(0)
    df["rbi"] = pd.to_numeric(df["rbi"], errors="coerce").fillna(0)
    df["avg"] = pd.to_numeric(df["avg"], errors="coerce").fillna(0)
    df["war"] = ((df["ops"] - 0.650) * 8 + df["hr"] * 0.03 + df["rbi"] * 0.01 + (df["avg"] - 0.250) * 10).round(2)
    df["war"] = df["war"].clip(lower=0)
    return df.sort_values("war", ascending=False)


def calculate_team_war():
    df = calculate_batter_war()
    team_df = df.groupby("team", as_index=False)["war"].sum()
    return team_df.sort_values("war", ascending=False)
