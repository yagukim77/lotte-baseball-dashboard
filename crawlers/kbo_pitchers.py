import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

NAVER_URLS = [
    "https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2025&tab=hitter",
    "https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter",
]

KBO_URLS = [
    "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=OPS_RT",
    "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HIT_CN",
]

TEAM_MAP = {
    "LOTTE": "롯데", "DOOSAN": "두산", "NC": "NC", "SSG": "SSG",
    "SAMSUNG": "삼성", "LG": "LG", "KIA": "KIA", "HANWHA": "한화",
    "KT": "KT", "KIWOOM": "키움",
}

KBO_EXPECTED = {"선수명", "팀명", "AVG", "HR", "RBI", "OPS"}


def _clean_num(v, default=0):
    try:
        s = str(v).strip().replace(",", "")
        if s in ["", "-", "nan", "None"]:
            return default
        return float(s)
    except Exception:
        return default


def _parse_naver_text(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    lines = [x.strip() for x in soup.get_text("\n", strip=True).splitlines() if x.strip()]

    rows = []
    # 이름 / 팀 / 타율 / 경기 / 타수 / 안타 / 홈런 / ... / 타점 / ... / 출루율 같은 형태를 최대한 보수적으로 추출
    for i, line in enumerate(lines):
        team_match = re.search(r"\b(LG|KIA|NC|LOTTE|DOOSAN|SSG|SAMSUNG|HANWHA|KT|KIWOOM)\b", line)
        avg_match = re.search(r"\b0\.\d{3}\b", line)

        if not team_match or not avg_match:
            continue

        parts = line.split()
        if len(parts) < 3:
            continue

        team_en = team_match.group(1)
        avg = float(avg_match.group(0))

        # 이름은 팀명 앞 문자열에서 추정
        before_team = line.split(team_en)[0].strip()
        player = re.sub(r"^\d+\s*", "", before_team).strip()
        if not player:
            continue

        nums = re.findall(r"\b\d+\b", line)
        hr = int(nums[4]) if len(nums) >= 5 else 0
        rbi = int(nums[7]) if len(nums) >= 8 else 0

        # 네이버 텍스트 구조가 바뀌면 OPS는 프록시로 계산
        ops = round(min(1.500, avg + (hr * 0.02) + (rbi * 0.003) + 0.200), 3)

        rows.append({
            "player": player,
            "team": TEAM_MAP.get(team_en, team_en),
            "avg": avg,
            "hr": hr,
            "rbi": rbi,
            "ops": ops,
        })

    return pd.DataFrame(rows).drop_duplicates(subset=["player", "team"])


def _parse_kbo_tables() -> pd.DataFrame:
    for url in KBO_URLS:
        try:
            tables = pd.read_html(url, flavor="lxml")
        except Exception:
            continue

        for df in tables:
            cols = {str(c).strip() for c in df.columns}
            if KBO_EXPECTED.issubset(cols):
                df = df.rename(columns={
                    "선수명": "player",
                    "팀명": "team",
                    "AVG": "avg",
                    "HR": "hr",
                    "RBI": "rbi",
                    "OPS": "ops",
                })
                df = df[["player", "team", "avg", "hr", "rbi", "ops"]].copy()
                df["player"] = df["player"].astype(str).str.strip()
                df["team"] = df["team"].astype(str).str.strip()
                df["avg"] = df["avg"].apply(lambda x: _clean_num(x, 0.0))
                df["hr"] = df["hr"].apply(lambda x: int(_clean_num(x, 0)))
                df["rbi"] = df["rbi"].apply(lambda x: int(_clean_num(x, 0)))
                df["ops"] = df["ops"].apply(lambda x: _clean_num(x, 0.0))
                return df.drop_duplicates(subset=["player", "team"])
    return pd.DataFrame()


def crawl_players():
    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame()

    for url in NAVER_URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            if res.ok and res.text:
                df = _parse_naver_text(res.text)
                if not df.empty:
                    break
        except Exception:
            pass

    if df.empty:
        df = _parse_kbo_tables()

    if df.empty:
        df = pd.DataFrame(columns=["player", "team", "avg", "hr", "rbi", "ops"])

    df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/players_stats.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_players()
