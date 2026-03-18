import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEAM_PATTERN = r"(롯데|두산|NC|SSG|삼성|LG|KIA|한화|KT|키움)"
STADIUM_PATTERN = r"(사직|잠실|문학|대구|수원|광주|대전|창원|고척|울산|포항|청주)"


def detect_season_type(text: str) -> str:
    if "시범경기" in text:
        return "시범경기"
    if "포스트시즌" in text or "한국시리즈" in text or "플레이오프" in text or "준플레이오프" in text or "와일드카드" in text:
        return "가을야구"
    return "정규시즌"


def crawl_schedule():
    os.makedirs("data", exist_ok=True)

    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    season_type = detect_season_type(text)
    today = datetime.now().strftime("%Y-%m-%d")

    tables = []
    try:
        tables = pd.read_html(URL, flavor="lxml")
    except Exception:
        tables = []

    rows = []

    for df in tables:
        joined = " ".join(map(str, df.columns))
        if "경기" not in joined and "구장" not in joined and "시간" not in joined:
            continue

        for _, row in df.iterrows():
            row_text = " ".join([str(x) for x in row.tolist()])

            teams = re.findall(TEAM_PATTERN, row_text)
            if len(teams) < 2:
                continue

            stadium_match = re.search(STADIUM_PATTERN, row_text)
            time_match = re.search(r"(\d{1,2}:\d{2})", row_text)
            score_match = re.search(r"(\d+)\s*[:：]\s*(\d+)", row_text)

            away = teams[0]
            home = teams[1]

            game_status = ""
            result = ""
            home_score = None
            away_score = None

            if "우천취소" in row_text:
                game_status = "우천취소"
            elif "취소" in row_text:
                game_status = "취소"
            elif "예정" in row_text or time_match:
                game_status = "예정"
            elif score_match:
                game_status = "종료"

            if score_match:
                away_score = int(score_match.group(1))
                home_score = int(score_match.group(2))
                if home_score > away_score:
                    result = "W"
                elif home_score < away_score:
                    result = "L"
                else:
                    result = "D"

            rows.append({
                "date": today,
                "away": away,
                "home": home,
                "stadium": stadium_match.group(1) if stadium_match else "",
                "time": time_match.group(1) if time_match else "",
                "away_score": away_score,
                "home_score": home_score,
                "result": result,
                "status": game_status,
                "season_type": season_type,
            })

    out = pd.DataFrame(rows).drop_duplicates()
    out.to_csv("data/schedule.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/schedule.csv ({len(out)} rows)")


if __name__ == "__main__":
    crawl_schedule()
