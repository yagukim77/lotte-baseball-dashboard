import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEAMS = ["롯데", "LG", "두산", "KIA", "삼성", "한화", "NC", "SSG", "키움", "KT"]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def looks_like_player(token: str) -> bool:
    token = str(token).strip()
    if not token or token in TEAMS:
        return False
    if any(ch.isdigit() for ch in token):
        return False
    return 1 < len(token) <= 6


def crawl_probable_starters() -> pd.DataFrame:
    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = normalize_text(soup.get_text(" ", strip=True))

    games = []
    pattern = re.compile(r"(롯데|LG|두산|KIA|삼성|한화|NC|SSG|키움|KT)\s+(롯데|LG|두산|KIA|삼성|한화|NC|SSG|키움|KT)")
    for m in pattern.finditer(text):
        away, home = m.group(1), m.group(2)
        nearby = text[max(0, m.start()-80):m.end()+120]

        names = []
        for token in re.findall(r"[가-힣A-Za-z]{2,6}", nearby):
            if looks_like_player(token):
                names.append(token)
        names = [n for n in names if n not in [away, home]]

        away_starter = names[0] if len(names) >= 1 else ""
        home_starter = names[1] if len(names) >= 2 else ""

        games.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "away": away,
            "home": home,
            "away_starter": away_starter,
            "home_starter": home_starter,
        })

    df = pd.DataFrame(games).drop_duplicates(subset=["date", "away", "home"])
    return df


if __name__ == "__main__":
    df = crawl_probable_starters()
    df.to_csv("data/probable_starters.csv", index=False, encoding="utf-8-sig")
    print("saved: data/probable_starters.csv")
