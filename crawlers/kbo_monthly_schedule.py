import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEAM_PATTERN = r"(롯데|두산|NC|SSG|삼성|LG|KIA|한화|KT|키움)"
STADIUM_PATTERN = r"(사직|잠실|문학|대구|수원|광주|대전|창원|고척|울산|포항|청주)"


def detect_season_type(text: str) -> str:
    if "시범경기" in text:
        return "시범경기"
    if "포스트시즌" in text or "한국시리즈" in text or "플레이오프" in text or "준플레이오프" in text or "와일드카드" in text:
        return "가을야구"
    return "정규시즌"


def parse_month(year: int, month: int):
    params = {"date": f"{year}-{month:02d}-01"}
    res = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
    res.raise_for_status()
    html = res.text

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    season_type = detect_season_type(text)

    rows = []
    try:
        tables = pd.read_html(html, flavor="lxml")
    except Exception:
        tables = []

    for df in tables:
        for _, row in df.iterrows():
            row_text = " ".join([str(x) for x in row.tolist()])

            teams = re.findall(TEAM_PATTERN, row_text)
            if len(teams) < 2:
                continue

            date_match = re.search(rf"{year}\.(\d{{2}})\.(\d{{2}})", row_text)
            if date_match:
                game_date = f"{year}-{date_match.group(1)}-{date_match.group(2)}"
            else:
                game_date = f"{year}-{month:02d}-01"

            stadium_match = re.search(STADIUM_PATTERN, row_text)
            time_match = re.search(r"(\d{1,2}:\d{2})", row_text)
            score_match = re.search(r"(\d+)\s*[:：]\s*(\d+)", row_text)

            status = ""
            if "우천취소" in row_text:
                status = "우천취소"
            elif "취소" in row_text:
                status = "취소"
            elif score_match:
                status = "종료"
            else:
                status = "예정"

            rows.append({
                "date": game_date,
                "away": teams[0],
                "home": teams[1],
                "time": time_match.group(1) if time_match else "",
                "stadium": stadium_match.group(1) if stadium_match else "",
                "status": status,
                "season_type": season_type,
            })

    return pd.DataFrame(rows).drop_duplicates()


def build_year_schedule():
    os.makedirs("data", exist_ok=True)
    year = datetime.now().year

    frames = []
    for month in range(1, 13):
        try:
            df = parse_month(year, month)
            if not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"month parse failed: {year}-{month:02d} / {e}")

    if frames:
        out = pd.concat(frames, ignore_index=True).drop_duplicates()
    else:
        out = pd.DataFrame(columns=["date", "away", "home", "time", "stadium", "status", "season_type"])

    out.to_csv("data/monthly_schedule.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/monthly_schedule.csv ({len(out)} rows)")


if __name__ == "__main__":
    build_year_schedule()
