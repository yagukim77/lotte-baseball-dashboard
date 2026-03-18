import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}

EXPECTED_COLS = ["선수명", "팀명", "ERA", "G", "W", "L", "SV"]


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


def crawl_pitchers():
    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    html = res.text

    df = _find_table_with_columns(html)

    # fallback: 혹시 read_html이 실패하면 soup 텍스트 확인만 하고 빈 파일 저장
    if df is None:
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        if "투수기록" not in page_text or "선수명" not in page_text:
            print("pitcher page loaded but record text not found")
        else:
            print("pitcher page loaded, but html table parsing failed")

        empty_df = pd.DataFrame(
            columns=["player", "team", "era", "game", "win", "lose", "save"]
        )
        empty_df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
        print("saved empty: data/pitcher_stats.csv")
        return

    # 컬럼명 정리
    df = df.rename(columns={
        "선수명": "player",
        "팀명": "team",
        "ERA": "era",
        "G": "game",
        "W": "win",
        "L": "lose",
        "SV": "save",
    })

    keep_cols = ["player", "team", "era", "game", "win", "lose", "save"]
    df = df[keep_cols].copy()

    df["player"] = df["player"].astype(str).str.strip()
    df["team"] = df["team"].astype(str).str.strip()
    df["era"] = df["era"].apply(lambda x: _clean_num(x, 4.50))
    df["game"] = df["game"].apply(lambda x: int(_clean_num(x, 0)))
    df["win"] = df["win"].apply(lambda x: int(_clean_num(x, 0)))
    df["lose"] = df["lose"].apply(lambda x: int(_clean_num(x, 0)))
    df["save"] = df["save"].apply(lambda x: int(_clean_num(x, 0)))

    df = df[df["player"].notna() & (df["player"] != "")]
    df = df.drop_duplicates(subset=["player", "team"])

    df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/pitcher_stats.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_pitchers()
