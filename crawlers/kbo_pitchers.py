import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def crawl_pitchers():
    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.select_one("table.tData")
    if table is None:
        raise ValueError("투수 기록 테이블을 찾지 못했습니다.")

    rows = table.select("tbody tr")
    data = []
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.select("td")]
        if len(cols) < 8:
            continue
        try:
            data.append({
                "player": cols[1],
                "team": cols[2],
                "era": float(cols[3]) if cols[3] not in ["-", ""] else 4.50,
                "game": int(cols[4]) if str(cols[4]).isdigit() else 0,
                "win": int(cols[5]) if str(cols[5]).isdigit() else 0,
                "lose": int(cols[6]) if str(cols[6]).isdigit() else 0,
                "save": int(cols[7]) if str(cols[7]).isdigit() else 0,
            })
        except Exception:
            continue
    pd.DataFrame(data).to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print("saved: data/pitcher_stats.csv")


if __name__ == "__main__":
    crawl_pitchers()
