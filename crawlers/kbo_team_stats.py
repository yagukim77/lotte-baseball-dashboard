import os
import pandas as pd

def build_team_stats():
    os.makedirs("data", exist_ok=True)

    players = pd.read_csv("data/players_stats.csv") if os.path.exists("data/players_stats.csv") else pd.DataFrame()
    pitchers = pd.read_csv("data/pitcher_stats.csv") if os.path.exists("data/pitcher_stats.csv") else pd.DataFrame()

    if players.empty and pitchers.empty:
        pd.DataFrame(columns=["team", "avg", "era", "team_ops"]).to_csv(
            "data/team_stats.csv", index=False, encoding="utf-8-sig"
        )
        print("saved empty: data/team_stats.csv")
        return

    out = pd.DataFrame()

    if not players.empty and {"team", "avg", "ops"}.issubset(players.columns):
        players["avg"] = pd.to_numeric(players["avg"], errors="coerce").fillna(0)
        players["ops"] = pd.to_numeric(players["ops"], errors="coerce").fillna(0)
        out = players.groupby("team", as_index=False).agg(avg=("avg", "mean"), team_ops=("ops", "mean"))

    if not pitchers.empty and {"team", "era"}.issubset(pitchers.columns):
        pitchers["era"] = pd.to_numeric(pitchers["era"], errors="coerce").fillna(4.50)
        pitch = pitchers.groupby("team", as_index=False).agg(era=("era", "mean"))
        out = pitch if out.empty else out.merge(pitch, on="team", how="outer")

    out.to_csv("data/team_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/team_stats.csv ({len(out)} rows)")

if __name__ == "__main__":
    build_team_stats()
