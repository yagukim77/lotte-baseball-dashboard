import pandas as pd

DEFAULT_LINEUP_OPS = 0.700

def estimate_lineup_strength(team: str, lineup_names: list[str] | None = None) -> float:
    try:
        df = pd.read_csv("data/players_stats.csv").copy()
    except Exception:
        return 4.5

    df["ops"] = pd.to_numeric(df.get("ops"), errors="coerce").fillna(0.700)
    df["team"] = df.get("team", "").astype(str)
    team_df = df[df["team"] == str(team)].copy()
    if team_df.empty:
        return 4.5

    if lineup_names:
        lineup_set = {str(x).strip() for x in lineup_names if str(x).strip()}
        picked = team_df[team_df["player"].astype(str).isin(lineup_set)].copy()
        if len(picked) >= 5:
            avg_ops = picked["ops"].mean()
        else:
            avg_ops = team_df.sort_values("ops", ascending=False).head(9)["ops"].mean()
    else:
        avg_ops = team_df.sort_values("ops", ascending=False).head(9)["ops"].mean()

    avg_ops = float(avg_ops) if pd.notna(avg_ops) else DEFAULT_LINEUP_OPS
    return round(max(2.5, avg_ops * 5.8), 2)


def get_default_lineup(team: str, top_n: int = 9) -> list[str]:
    try:
        df = pd.read_csv("data/players_stats.csv").copy()
    except Exception:
        return []

    df["ops"] = pd.to_numeric(df.get("ops"), errors="coerce").fillna(0.700)
    team_df = df[df["team"].astype(str) == str(team)].sort_values("ops", ascending=False).head(top_n)
    return team_df["player"].astype(str).tolist()
