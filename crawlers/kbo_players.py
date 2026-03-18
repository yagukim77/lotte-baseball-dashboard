import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://eng.koreabaseball.com/stats/BattingLeaders.aspx"
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

LINE_RE = re.compile(
    r"^\d+\s+([A-Z][A-Za-z'\- ]+?)\s+"
    r"(LG|KIA|NC|LOTTE|DOOSAN|SSG|SAMSUNG|HANWHA|KT|KIWOOM)\s+"
    r"([0-9.]+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+\d+\s+(\d+)\s+"
)

def crawl_players():
    os.makedirs("data", exist_ok=True)

    res = requests.get(URL, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    lines = [x.strip() for x in soup.get_text("\n", strip=True).splitlines() if x.strip()]

    rows = []
    for line in lines:
        m = LINE_RE.match(line)
        if not m:
            continue
        player_en = m.group(1).strip()
        team_en = m.group(2).strip()
        avg = float(m.group(3))
        hr = int(m.group(4))
        rbi = int(m.group(5))

        # OPS는 leaders 페이지에 직접 없어서 임시 근사치
        # AVG + HR/RBI 보정으로 최소 동작 보장
        ops_proxy = round(min(1.500, avg + (hr * 0.02) + (rbi * 0.003) + 0.200), 3)

        rows.append({
            "player": player_en,
            "team": TEAM_MAP.get(team_en, team_en),
            "avg": avg,
            "hr": hr,
            "rbi": rbi,
            "ops": ops_proxy,
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["player", "team"])
    df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/players_stats.csv ({len(df)} rows)")

if __name__ == "__main__":
    crawl_players()
