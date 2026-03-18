import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}

TEAM_LIST = ["롯데", "LG", "두산", "KIA", "삼성", "한화", "NC", "SSG", "키움", "KT"]

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()

def extract_games_from_text(text: str):
    text = normalize_text(text)
    teams = "|".join(TEAM_LIST)
    status_candidates = [
        "경기전", "예정", "취소", "우천취소", "종료",
        "1회", "2회", "3회", "4회", "5회", "6회", "7회", "8회", "9회", "연장"
    ]

    games = []
    team_matches = re.finditer(rf"({teams})\s+({teams})", text)

    for m in team_matches:
        away = m.group(1)
        home = m.group(2)

        nearby = text[m.start():m.start() + 120]
        score_match = re.search(r"(\d+)\s*[:：]\s*(\d+)", nearby)

        status = "경기전"
        for s in status_candidates:
            if s in nearby:
                status = s
                break

        away_score = 0
        home_score = 0
        if score_match:
            away_score = int(score_match.group(1))
            home_score = int(score_match.group(2))

        games.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "away": away,
            "home": home,
            "away_score": away_score,
            "home_score": home_score,
            "status": status,
        })

    uniq = []
    seen = set()
    for g in games:
        key = (g["away"], g["home"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(g)

    return uniq

def crawl_live_scores() -> pd.DataFrame:
    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    games = extract_games_from_text(text)
    return pd.DataFrame(games)

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
    df = crawl_live_scores()
    df.to_csv("data/live_score.csv", index=False, encoding="utf-8-sig")
    print("saved: data/live_score.csv")
