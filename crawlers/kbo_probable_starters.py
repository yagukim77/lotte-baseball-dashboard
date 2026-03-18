import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEAM_PATTERN = r"(롯데|두산|NC|SSG|삼성|LG|KIA|한화|KT|키움)"


def crawl_probable_starters():
    os.makedirs("data", exist_ok=True)

    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    today = datetime.now().strftime("%Y-%m-%d")
    teams = re.findall(TEAM_PATTERN, text)

    rows = []
    for i in range(0, len(teams) - 1, 2):
        away = teams[i]
        home = teams[i + 1]
        rows.append({
            "date": today,
            "away": away,
            "home": home,
            "away_starter": "",
            "home_starter": "",
        })

    out = pd.DataFrame(rows).drop_duplicates()
    out.to_csv("data/probable_starters.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/probable_starters.csv ({len(out)} rows)")


if __name__ == "__main__":
    crawl_probable_starters()
