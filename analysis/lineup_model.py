import pandas as pd


def lineup_attack_score(players: list[str], is_home: bool = True) -> float:
    try:
        df = pd.read_csv("data/players_stats.csv").copy()
    except Exception:
        return 4.5

    if df.empty or "player" not in df.columns or "ops" not in df.columns:
        return 4.5

    df["player"] = df["player"].astype(str).str.strip()
    df["ops"] = pd.to_numeric(df["ops"], errors="coerce").fillna(0)

    selected = df[df["player"].isin(players)].copy()
    if selected.empty:
        return 4.5

    avg_ops = selected["ops"].mean()

    # 홈/원정 라인업 입력은 나중에 split 데이터 생기면 더 고도화 가능
    base = avg_ops * 5.6
    if is_home:
        base *= 1.01
    else:
        base *= 0.99

    return round(max(2.5, base), 2)
