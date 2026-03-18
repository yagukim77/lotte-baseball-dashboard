import os
import pandas as pd

CANDIDATE_URLS = [
    "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=ERA_RT",
    "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=W_CN",
    "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=SV_CN",
]

EXPECTED = {"선수명", "팀명", "ERA", "G", "W", "L", "SV"}


def _clean_num(v, default=0):
    try:
        s = str(v).strip().replace(",", "")
        if s in ["", "-", "nan", "None"]:
            return default
        return float(s)
    except Exception:
        return default


def _find_table():
    for url in CANDIDATE_URLS:
        try:
            tables = pd.read_html(url, flavor="lxml")
        except Exception:
            continue

        for df in tables:
            cols = {str(c).strip() for c in df.columns}
            if EXPECTED.issubset(cols):
                return df.copy()

    return None


def crawl_pitchers():
    os.makedirs("data", exist_ok=True)

    df = _find_table()

    if df is None:
        print("pitchers table parsing failed")
        if not os.path.exists("data/pitcher_stats.csv"):
            pd.DataFrame(columns=["player", "team", "era", "game", "win", "lose", "save"]).to_csv(
                "data/pitcher_stats.csv", index=False, encoding="utf-8-sig"
            )
        return

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

    df = df.dropna(subset=["player", "team"])
    df = df[df["player"] != ""]
    df = df.drop_duplicates(subset=["player", "team"])

    df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print(f"saved: data/pitcher_stats.csv ({len(df)} rows)")


if __name__ == "__main__":
    crawl_pitchers()
