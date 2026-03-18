import os
import pandas as pd

URLS = [
    "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx",
    "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx",
]

def crawl_standings():
    os.makedirs("data", exist_ok=True)

    df = None

    for url in URLS:
        try:
            tables = pd.read_html(url, flavor="lxml")
            for t in tables:
                cols = [str(c).strip() for c in t.columns]
                text = " ".join(cols)
                if "팀명" in text or "순위" in text:
                    df = t.copy()
                    break
            if df is not None:
                break
        except Exception as e:
            print(f"standings parse failed: {url} / {e}")

    if df is None:
        print("standings table parsing failed")
        if not os.path.exists("data/kbo_standings.csv"):
            pd.DataFrame().to_csv("data/kbo_standings.csv", index=False, encoding="utf-8-sig")
        return

    df.to_csv("data/kbo_standings.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/kbo_standings.csv ({len(df)} rows)")

if __name__ == "__main__":
    crawl_standings()
