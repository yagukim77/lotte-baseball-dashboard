import os
import pandas as pd


def build_games():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists("data/monthly_schedule.csv"):
        pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"]).to_csv(
            "data/games.csv", index=False, encoding="utf-8-sig"
        )
        print("monthly_schedule.csv missing -> saved empty games.csv")
        return

    try:
        df = pd.read_csv("data/monthly_schedule.csv")
    except Exception:
        df = pd.DataFrame()

    if df.empty or not {"date", "home", "away", "status"}.issubset(df.columns):
        pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"]).to_csv(
            "data/games.csv", index=False, encoding="utf-8-sig"
        )
        print("monthly_schedule invalid -> saved empty games.csv")
        return

    if "home_score" not in df.columns:
        df["home_score"] = None
    if "away_score" not in df.columns:
        df["away_score"] = None

    ended = df[df["status"] == "종료"].copy()

    if ended.empty:
        pd.DataFrame(columns=["date", "home", "away", "runs", "allowed", "result"]).to_csv(
            "data/games.csv", index=False, encoding="utf-8-sig"
        )
        print("no ended games -> saved empty games.csv")
        return

    ended["runs"] = pd.to_numeric(ended["home_score"], errors="coerce").fillna(0).astype(int)
    ended["allowed"] = pd.to_numeric(ended["away_score"], errors="coerce").fillna(0).astype(int)

    def calc_result(row):
        if row["runs"] > row["allowed"]:
            return "W"
        if row["runs"] < row["allowed"]:
            return "L"
        return "D"

    ended["result"] = ended.apply(calc_result, axis=1)

    out = ended[["date", "home", "away", "runs", "allowed", "result"]].copy()
    out.to_csv("data/games.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/games.csv ({len(out)} rows)")


if __name__ == "__main__":
    build_games()
