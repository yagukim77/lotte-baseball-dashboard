import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}

EXPECTED_COLS = ["선수명", "팀명", "AVG", "HR", "RBI", "OPS"]


def _clean_num(value, default=0.0):
    try:
        s = str(value).strip().replace(",", "")
        if s in ["-", "", "nan", "None"]:
            return default
        return float(s)
    except Exception:
        return default


def _find_table_with_columns(html: str):
    try:
        tables = pd.read_html(html)
    except Exception:
        return None

    for df in tables:
        cols = [str(c).strip() for c in df.columns]
        if all(col in cols for col in EXPECTED_COLS):
            return df.copy()

    return None


def crawl_players():
    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    html = res.text

    df = _find_table_with_columns(html)

    if df is None:
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        if "타자" not in page_text or "선수명" not in page_text:
            print("hitter page loaded but record text not found")
        else:
            print("hitter page loaded, but html table parsing failed")

        empty_df = pd.DataFrame(
            columns=["player", "team", "avg", "hr", "rbi", "ops"]
        )
        empty_df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
        print("saved empty: data/players_stats.csv")
        return

    df = df.rename(columns={
        "선수명": "player",
        "팀명": "team",
        "AVG": "avg",
        "HR": "hr",
        "RBI": "rbi",
        "OPS": "ops",
    })

    keep_cols = ["player", "team", "avg", "hr", "rbi", "ops"]
    df = df[keep_cols].copy()

    df["player"] = df["player"].astype(str).str.strip()
    df["team"] = df["team"].astype(str).str.strip()
    df["avg"] = df["avg"].apply(lambda x: _clean_num(x, 0.0))
    df["hr"] = df["hr"].apply(lambda x: int(_clean_num(x, 0)))
    df["rbi"] = df["rbi"].apply(lambda x: int(_clean_num(x, 0)))
    df["ops"] = df["ops"].apply(lambda x: _clean_num(x, 0.0))

    df = df[df["player"].notna() & (df["player"] != "")]
    df = df.drop_duplicates(subset=["player", "team"])

    df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/players_stats.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_players()
