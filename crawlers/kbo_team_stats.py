import os
import pandas as pd


def build_team_stats():
    os.makedirs("data", exist_ok=True)

    players = pd.DataFrame()
    pitchers = pd.DataFrame()

    if os.path.exists("data/players_stats.csv"):
        try:
            players = pd.read_csv("data/players_stats.csv")
        except Exception:
            players = pd.DataFrame()

    if os.path.exists("data/pitcher_stats.csv"):
        try:
            pitchers = pd.read_csv("data/pitcher_stats.csv")
        except Exception:
            pitchers = pd.DataFrame()

    team_hit = pd.DataFrame(columns=["team", "avg", "team_ops"])
    team_pitch = pd.DataFrame(columns=["team", "era"])

    if not players.empty and {"team", "avg", "ops"}.issubset(players.columns):
        players["avg"] = pd.to_numeric(players["avg"], errors="coerce").fillna(0)
        players["ops"] = pd.to_numeric(players["ops"], errors="coerce").fillna(0)
        team_hit = players.groupby("team", as_index=False).agg(
            avg=("avg", "mean"),
            team_ops=("ops", "mean"),
        )

    if not pitchers.empty and {"team", "era"}.issubset(pitchers.columns):
        pitchers["era"] = pd.to_numeric(pitchers["era"], errors="coerce").fillna(4.50)
        team_pitch = pitchers.groupby("team", as_index=False).agg(
            era=("era", "mean"),
        )

    if team_hit.empty and team_pitch.empty:
        out = pd.DataFrame(columns=["team", "avg", "era", "team_ops"])
    else:
        out = pd.merge(team_hit, team_pitch, on="team", how="outer")

    out.to_csv("data/team_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/team_stats.csv ({len(out)} rows)")


if __name__ == "__main__":
    build_team_stats()
