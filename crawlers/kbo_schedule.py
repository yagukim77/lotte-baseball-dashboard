import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://eng.koreabaseball.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

TEAM_MAP = {
    "LOTTE": "롯데",
    "DOOSAN": "두산",
    "NC": "NC",
    "SSG": "SSG",
    "SAMSUNG": "삼성",
    "LG": "LG",
    "KIA": "KIA",
    "HANWHA": "한화",
    "KT": "KT",
    "KIWOOM": "키움",
}

STADIUM_MAP = {
    "SAJIK": "사직",
    "CHANGWON": "창원",
    "SUWON": "수원",
    "DAEJEON": "대전",
    "MUNHAK": "문학",
    "DAEGU": "대구",
    "JAMSIL": "잠실",
    "GWANGJU": "광주",
    "GOCHUK": "고척",
}

def detect_season_type():
    # 지금 시점은 시범경기, 정규시즌 개막 후엔 영문 메인도 해당 일정으로 바뀜
    now = datetime.now()
    if now.month == 3 and now.day < 28:
        return "시범경기"
    return "정규시즌"

def crawl_schedule():
    os.makedirs("data", exist_ok=True)

    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    lines = [x.strip() for x in soup.get_text("\n", strip=True).splitlines() if x.strip()]

    season_type = detect_season_type()
    current_date = None
    rows = []

    i = 0
    while i < len(lines):
        line = lines[i]

        date_m = re.match(r"^(MON|TUE|WED|THU|FRI|SAT|SUN)\s+([A-Z]{3})\s+(\d{1,2})$", line)
        if date_m:
            month_map = {
                "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
            }
            mm = month_map[date_m.group(2)]
            dd = int(date_m.group(3))
            yyyy = datetime.now().year
            current_date = f"{yyyy}-{mm:02d}-{dd:02d}"
            i += 1
            continue

        if line in TEAM_MAP and i + 2 < len(lines):
            away = TEAM_MAP.get(line, line)
            middle = lines[i + 1]
            third = lines[i + 2]

            if middle == "VS":
                # 예정 경기: third = "LOTTE SAJIK 13:00"
                parts = third.split()
                if len(parts) >= 2:
                    home = TEAM_MAP.get(parts[0], parts[0])
                    stadium = STADIUM_MAP.get(parts[1], parts[1])
                    game_time = parts[2] if len(parts) >= 3 else ""
                    rows.append({
                        "date": current_date,
                        "away": away,
                        "home": home,
                        "stadium": stadium,
                        "time": game_time,
                        "away_score": None,
                        "home_score": None,
                        "result": "",
                        "status": "예정",
                        "season_type": season_type,
                    })
                    i += 3
                    continue

            if re.match(r"^\d+:\d+$", middle):
                # 결과 경기: third = "NC CHANGWON"
                parts = third.split()
                if len(parts) >= 2:
                    home = TEAM_MAP.get(parts[0], parts[0])
                    stadium = STADIUM_MAP.get(parts[1], parts[1])

                    away_score = int(middle.split(":")[0])
                    home_score = int(middle.split(":")[1])

                    result = "W" if home_score > away_score else ("L" if home_score < away_score else "D")

                    rows.append({
                        "date": current_date,
                        "away": away,
                        "home": home,
                        "stadium": stadium,
                        "time": "",
                        "away_score": away_score,
                        "home_score": home_score,
                        "result": result,
                        "status": "종료",
                        "season_type": season_type,
                    })
                    i += 3
                    continue
        i += 1

    df = pd.DataFrame(rows).drop_duplicates()
    df.to_csv("data/schedule.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/schedule.csv ({len(df)} rows)")

if __name__ == "__main__":
    crawl_schedule()
