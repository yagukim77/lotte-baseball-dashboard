import pandas as pd

TEAM_ALIASES = {
    "KIA": ["KIA", "기아"],
    "KT": ["KT", "케이티"],
    "LG": ["LG"],
    "NC": ["NC"],
    "SSG": ["SSG"],
    "두산": ["두산"],
    "롯데": ["롯데"],
    "삼성": ["삼성"],
    "키움": ["키움"],
    "한화": ["한화"],
}


def normalize_team(team: str) -> str:
    if not team:
        return ""
    t = str(team).strip()
    for key, vals in TEAM_ALIASES.items():
        if t in vals:
            return key
    return t


def get_probable_starters(home: str, away: str):
    try:
        df = pd.read_csv("data/probable_starters.csv").copy()
    except Exception:
        return "", ""

    if df.empty:
        return "", ""

    if not {"home", "away"}.issubset(df.columns):
        return "", ""

    df["home"] = df["home"].astype(str).apply(normalize_team)
    df["away"] = df["away"].astype(str).apply(normalize_team)

    target = df[
        (df["home"] == normalize_team(home)) &
        (df["away"] == normalize_team(away))
    ]

    if target.empty:
        return "", ""

    row = target.iloc[0]
    away_starter = str(row["away_starter"]).strip() if "away_starter" in row else ""
    home_starter = str(row["home_starter"]).strip() if "home_starter" in row else ""
    return away_starter, home_starter
