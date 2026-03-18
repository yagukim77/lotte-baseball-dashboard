import os
import pandas as pd

def build_games():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists("data/schedule.csv"):
        out = pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"])
        out.to_csv("data/games.csv", index=False, encoding="utf-8-sig")
        return

    df = pd.read_csv("data/schedule.csv")
    if df.empty or "status" not in df.columns:
        out = pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"])
        out.to_csv("data/games.csv", index=False, encoding="utf-8-sig")
        return

    ended = df[df["status"] == "종료"].copy()
    if ended.empty:
        out = pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"])
        out.to_csv("data/games.csv", index=False, encoding="utf-8-sig")
        return

    ended["runs"] = pd.to_numeric(ended["home_score"], errors="coerce").fillna(0).astype(int)
    ended["allowed"] = pd.to_numeric(ended["away_score"], errors="coerce").fillna(0).astype(int)
    ended["result"] = ended.apply(
        lambda r: "W" if r["runs"] > r["allowed"] else ("L" if r["runs"] < r["allowed"] else "D"),
        axis=1
    )

    out = ended[["date", "home", "away", "runs", "allowed", "result"]].copy()
    out.to_csv("data/games.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/games.csv ({len(out)} rows)")

if __name__ == "__main__":
    build_games()
