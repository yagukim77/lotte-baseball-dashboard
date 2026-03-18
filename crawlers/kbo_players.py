import os
import pandas as pd

CANDIDATE_URLS = [
    "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=OPS_RT",
    "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HIT_CN",
    "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HR_CN",
]

EXPECTED = {"선수명", "팀명", "AVG", "HR", "RBI", "OPS"}

def _clean_num(v, default=0):
    try:
        s = str(v).strip().replace(",", "")
        if s in ["", "-", "nan", "None"]:
            return default
        return float(s)
    except Exception:
        return default

def _find_table():
    for url in CANDIDATE_URLS:
        try:
            tables = pd.read_html(url, flavor="lxml")
            for df in tables:
                cols = {str(c).strip() for c in df.columns}
                if EXPECTED.issubset(cols):
                    return df.copy()
        except Exception as e:
            print(f"players parse failed: {url} / {e}")
    return None

def crawl_players():
    os.makedirs("data", exist_ok=True)

    df = _find_table()

    if df is None:
        print("players table parsing failed")
        if not os.path.exists("data/players_stats.csv"):
            pd.DataFrame(columns=["player", "team", "avg", "hr", "rbi", "ops"]).to_csv(
                "data/players_stats.csv", index=False, encoding="utf-8-sig"
            )
        return

    df = df.rename(columns={
        "선수명": "player",
        "팀명": "team",
        "AVG": "avg",
        "HR": "hr",
        "RBI": "rbi",
        "OPS": "ops",
    })

    df = df[["player", "team", "avg", "hr", "rbi", "ops"]].copy()

    df["player"] = df["player"].astype(str).str.strip()
    df["team"] = df["team"].astype(str).str.strip()
    df["avg"] = df["avg"].apply(lambda x: _clean_num(x, 0.0))
    df["hr"] = df["hr"].apply(lambda x: int(_clean_num(x, 0)))
    df["rbi"] = df["rbi"].apply(lambda x: int(_clean_num(x, 0)))
    df["ops"] = df["ops"].apply(lambda x: _clean_num(x, 0.0))

    df = df.dropna(subset=["player", "team"])
    df = df[df["player"] != ""]
    df = df.drop_duplicates(subset=["player", "team"])

    if len(df) == 0:
        print("players parsed but empty; keep old file if exists")
        if not os.path.exists("data/players_stats.csv"):
            df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
        return

    df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/players_stats.csv ({len(df)} rows)")

if __name__ == "__main__":
    crawl_players()
