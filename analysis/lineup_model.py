import pandas as pd

def lineup_attack_score(players: list[str]) -> float:
    try:
        df = pd.read_csv("data/players_stats.csv").copy()
    except Exception:
        return 4.5

    if df.empty or "player" not in df.columns or "ops" not in df.columns:
        return 4.5

    df["player"] = df["player"].astype(str).str.strip()
    df["ops"] = pd.to_numeric(df["ops"], errors="coerce").fillna(0)

    selected = df[df["player"].isin(players)]
    if selected.empty:
        return 4.5

    avg_ops = selected["ops"].mean()
    return round(max(2.5, avg_ops * 5.5), 2)
