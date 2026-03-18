import os
import pandas as pd
from datetime import datetime

def crawl_probable_starters():
    os.makedirs("data", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists("data/schedule.csv"):
        df = pd.read_csv("data/schedule.csv")
        if not df.empty and {"home", "away"}.issubset(df.columns):
            out = df[["away", "home"]].drop_duplicates().copy()
            out["date"] = today
            out["away_starter"] = ""
            out["home_starter"] = ""
            out = out[["date", "away", "home", "away_starter", "home_starter"]]
            out.to_csv("data/probable_starters.csv", index=False, encoding="utf-8-sig")
            print(f"saved: data/probable_starters.csv ({len(out)} rows)")
            return

    out = pd.DataFrame(columns=["date", "away", "home", "away_starter", "home_starter"])
    out.to_csv("data/probable_starters.csv", index=False, encoding="utf-8-sig")
    print("saved empty: data/probable_starters.csv")

if __name__ == "__main__":
    crawl_probable_starters()
