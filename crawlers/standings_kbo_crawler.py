import os
import pandas as pd

URLS = [
    "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx",
    "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx",
]

OUTPUT_PATH = "data/kbo_standings.csv"


def _read_tables(url: str):
    # 1차: lxml
    try:
        return pd.read_html(url, flavor="lxml")
    except Exception as e:
        print(f"[lxml fail] {url} / {e}")

    # 2차: html5lib
    try:
        return pd.read_html(url, flavor="html5lib")
    except Exception as e:
        print(f"[html5lib fail] {url} / {e}")

    return []


def _is_standings_table(df: pd.DataFrame) -> bool:
    cols = [str(c).strip() for c in df.columns]
    text = " ".join(cols)

    keywords = ["팀명", "순위", "승", "패", "승률"]
    score = sum(1 for k in keywords if k in text)

    return score >= 2


def crawl_standings():
    os.makedirs("data", exist_ok=True)

    result_df = None

    for url in URLS:
        tables = _read_tables(url)

        for t in tables:
            try:
                if _is_standings_table(t):
                    result_df = t.copy()
                    break
            except Exception as e:
                print(f"table check fail: {e}")

        if result_df is not None:
            break

    if result_df is None:
        print("standings table parsing failed")

        if not os.path.exists(OUTPUT_PATH):
            pd.DataFrame().to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
            print(f"saved empty: {OUTPUT_PATH}")
        else:
            print(f"keep existing file: {OUTPUT_PATH}")
        return

    # 컬럼명이 multi-index일 수도 있어서 평탄화
    if isinstance(result_df.columns, pd.MultiIndex):
        result_df.columns = [
            "_".join([str(x).strip() for x in col if str(x).strip() != ""]).strip("_")
            for col in result_df.columns
        ]

    # 완전 빈 행 제거
    result_df = result_df.dropna(how="all")

    # 중복 제거
    result_df = result_df.drop_duplicates()

    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"saved: {OUTPUT_PATH} ({len(result_df)} rows)")


if __name__ == "__main__":
    try:
        crawl_standings()
    except Exception as e:
        print(f"standings crawler fatal error: {e}")

        os.makedirs("data", exist_ok=True)
        if not os.path.exists(OUTPUT_PATH):
            pd.DataFrame().to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
            print(f"saved empty after fatal error: {OUTPUT_PATH}")
