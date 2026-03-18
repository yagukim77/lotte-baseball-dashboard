import os
import pandas as pd

def crawl_live_scores():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists("data/schedule.csv"):
        pd.DataFrame(columns=["date", "away", "home", "away_score", "home_score", "status"]).to_csv(
            "data/live_score.csv", index=False, encoding="utf-8-sig"
        )
        print("saved empty: data/live_score.csv")
        return pd.DataFrame()

    df = pd.read_csv("data/schedule.csv")
    if df.empty:
        df = pd.DataFrame(columns=["date", "away", "home", "away_score", "home_score", "status"])

    cols = ["date", "away", "home", "away_score", "home_score", "status"]
    out = df[cols].copy() if all(c in df.columns for c in cols) else pd.DataFrame(columns=cols)
    out.to_csv("data/live_score.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/live_score.csv ({len(out)} rows)")
    return out

def get_lotte_live_game():
    try:
        df = crawl_live_scores()
        if df.empty:
            return None
        target = df[(df["away"] == "롯데") | (df["home"] == "롯데")]
        if target.empty:
            return None
        return target.iloc[0].to_dict()
    except Exception:
        return None

if __name__ == "__main__":
    crawl_live_scores()
