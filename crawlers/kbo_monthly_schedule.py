import re
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

MONTHLY_URL = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def detect_season_type(text: str) -> str:
    text = str(text)
    if "시범" in text:
        return "시범경기"
    if any(x in text for x in ["포스트", "준플", "플레이오프", "한국시리즈", "와일드카드"]):
        return "가을야구"
    return "정규시즌"


def parse_month_schedule(year: int, month: int) -> pd.DataFrame:
    params = {"seriesId": 0, "date": f"{year}-{month:02d}-01"}
    res = requests.get(MONTHLY_URL, params=params, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    season_type = detect_season_type(text)
    rows = []
    teams = "롯데|LG|두산|KIA|삼성|한화|NC|SSG|키움|KT"
    for tr in soup.select("tr"):
        row_text = re.sub(r"\s+", " ", tr.get_text(" ", strip=True))
        tm = re.findall(rf"({teams})", row_text)
        if len(tm) < 2:
            continue
        date_match = re.search(rf"{year}[./-](\d{{2}})[./-](\d{{2}})", row_text)
        if not date_match:
            continue
        time_match = re.search(r"(\d{1,2}:\d{2})", row_text)
        rows.append({
            "date": f"{year}-{int(date_match.group(1)):02d}-{int(date_match.group(2)):02d}",
            "away": tm[0],
            "home": tm[1],
            "time": time_match.group(1) if time_match else "",
            "season_type": season_type,
        })
    return pd.DataFrame(rows).drop_duplicates()


def build_schedule_for_months() -> pd.DataFrame:
    now = datetime.now()
    targets = [(now.year, now.month)]
    if now.month == 12:
        targets.append((now.year + 1, 1))
    else:
        targets.append((now.year, now.month + 1))
    frames = []
    for y, m in targets:
        try:
            frames.append(parse_month_schedule(y, m))
        except Exception as e:
            print(f"monthly schedule parse failed: {y}-{m:02d} / {e}")
    if not frames:
        return pd.DataFrame(columns=["date", "away", "home", "time", "season_type"])
    return pd.concat(frames, ignore_index=True).drop_duplicates()


if __name__ == "__main__":
    df = build_schedule_for_months()
    df.to_csv("data/monthly_schedule.csv", index=False, encoding="utf-8-sig")
    print("saved: data/monthly_schedule.csv")
