import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

NAVER_URLS = [
    "https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2025&tab=pitcher",
    "https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher",
]

KBO_URLS = [
    "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=ERA_RT",
    "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=W_CN",
]

TEAM_MAP = {
    "LOTTE": "롯데", "DOOSAN": "두산", "NC": "NC", "SSG": "SSG",
    "SAMSUNG": "삼성", "LG": "LG", "KIA": "KIA", "HANWHA": "한화",
    "KT": "KT", "KIWOOM": "키움",
}

KBO_EXPECTED = {"선수명", "팀명", "ERA", "G", "W", "L", "SV"}


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
    for line in lines:
        team_match = re.search(r"\b(LG|KIA|NC|LOTTE|DOOSAN|SSG|SAMSUNG|HANWHA|KT|KIWOOM)\b", line)
        era_match = re.search(r"\b\d+\.\d{2}\b", line)

        if not team_match or not era_match:
            continue

        team_en = team_match.group(1)
        era = float(era_match.group(0))
        before_team = line.split(team_en)[0].strip()
        player = re.sub(r"^\d+\s*", "", before_team).strip()
        if not player:
            continue

        nums = re.findall(r"\b\d+\b", line)
        game = int(nums[1]) if len(nums) >= 2 else 0
        win = int(nums[2]) if len(nums) >= 3 else 0
        lose = int(nums[3]) if len(nums) >= 4 else 0
        save = int(nums[4]) if len(nums) >= 5 else 0

        rows.append({
            "player": player,
            "team": TEAM_MAP.get(team_en, team_en),
            "era": era,
            "game": game,
            "win": win,
            "lose": lose,
            "save": save,
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
                    "ERA": "era",
                    "G": "game",
                    "W": "win",
                    "L": "lose",
                    "SV": "save",
                })
                df = df[["player", "team", "era", "game", "win", "lose", "save"]].copy()
                df["player"] = df["player"].astype(str).str.strip()
                df["team"] = df["team"].astype(str).str.strip()
                df["era"] = df["era"].apply(lambda x: _clean_num(x, 4.50))
                df["game"] = df["game"].apply(lambda x: int(_clean_num(x, 0)))
                df["win"] = df["win"].apply(lambda x: int(_clean_num(x, 0)))
                df["lose"] = df["lose"].apply(lambda x: int(_clean_num(x, 0)))
                df["save"] = df["save"].apply(lambda x: int(_clean_num(x, 0)))
                return df.drop_duplicates(subset=["player", "team"])
    return pd.DataFrame()


def crawl_pitchers():
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
        df = pd.DataFrame(columns=["player", "team", "era", "game", "win", "lose", "save"])

    df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/pitcher_stats.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_pitchers()
