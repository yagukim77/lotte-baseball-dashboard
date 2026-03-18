import os
import pandas as pd

def build_team_stats():
    os.makedirs("data", exist_ok=True)

    path = "data/players_stats.csv"
    out = "data/team_stats.csv"

    if not os.path.exists(path):
        pd.DataFrame(columns=["team", "team_ops"]).to_csv(out, index=False, encoding="utf-8-sig")
        return

    try:
        df = pd.read_csv(path)
    except Exception:
        pd.DataFrame(columns=["team", "team_ops"]).to_csv(out, index=False, encoding="utf-8-sig")
        return

    if df.empty or "team" not in df.columns or "ops" not in df.columns:
        pd.DataFrame(columns=["team", "team_ops"]).to_csv(out, index=False, encoding="utf-8-sig")
        return

    df["ops"] = pd.to_numeric(df["ops"], errors="coerce").fillna(0)
    team_df = df.groupby("team", as_index=False)["ops"].mean()
    team_df.columns = ["team", "team_ops"]

    team_df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"saved: {out} ({len(team_df)} rows)")

if __name__ == "__main__":
    build_team_stats()
