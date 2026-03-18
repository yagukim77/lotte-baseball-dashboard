import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def detect_season_type(text: str) -> str:
    if "시범경기" in text:
        return "시범경기"
    if "포스트시즌" in text or "한국시리즈" in text or "플레이오프" in text or "준플레이오프" in text or "와일드카드" in text:
        return "가을야구"
    return "정규시즌"


def crawl_standings():
    os.makedirs("data", exist_ok=True)

    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    season_type = detect_season_type(text)

    pattern = re.compile(
        r"(\d+)\s+(롯데|두산|NC|SSG|삼성|LG|KIA|한화|KT|키움)\s+"
        r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9.]+)\s+([0-9.]+)\s+"
        r"([0-9승무패]+)\s+([0-9승패무]+)\s+([0-9\-]+)\s+([0-9\-]+)"
    )

    rows = []
    for m in pattern.finditer(text):
        rows.append({
            "rank": int(m.group(1)),
            "team": m.group(2),
            "games": int(m.group(3)),
            "win": int(m.group(4)),
            "lose": int(m.group(5)),
            "draw": int(m.group(6)),
            "win_rate": float(m.group(7)),
            "gb": float(m.group(8)),
            "recent10": m.group(9),
            "streak": m.group(10),
            "home_record": m.group(11),
            "away_record": m.group(12),
            "season_type": season_type,
        })

    df = pd.DataFrame(rows)

    # team_stats.csv 있으면 avg/era 붙이기
    avg_vals = {}
    era_vals = {}
    if os.path.exists("data/team_stats.csv"):
        try:
            team_df = pd.read_csv("data/team_stats.csv")
            if {"team", "avg", "era"}.issubset(team_df.columns):
                avg_vals = dict(zip(team_df["team"], team_df["avg"]))
                era_vals = dict(zip(team_df["team"], team_df["era"]))
        except Exception:
            pass

    if not df.empty:
        df["avg"] = df["team"].map(avg_vals)
        df["era"] = df["team"].map(era_vals)

    df.to_csv("data/kbo_standings.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/kbo_standings.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_standings()
