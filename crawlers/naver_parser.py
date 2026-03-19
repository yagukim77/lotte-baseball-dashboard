from __future__ import annotations

from pathlib import Path
import pandas as pd
import re
from typing import List, Dict, Optional


TEAM_ALIASES = {
    "KIA": "KIA",
    "기아": "KIA",
    "한화": "한화",
    "롯데": "롯데",
    "두산": "두산",
    "LG": "LG",
    "엘지": "LG",
    "SSG": "SSG",
    "삼성": "삼성",
    "키움": "키움",
    "NC": "NC",
    "엔씨": "NC",
    "KT": "KT",
    "kt": "KT",
    "케이티": "KT",
}


def normalize_team(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None
    s = str(name).strip()
    return TEAM_ALIASES.get(s, s)


def safe_int(x):
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    return int(s) if s.isdigit() else None


def normalize_status(raw: Optional[str]) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    if "우천취소" in s:
        return "우천취소"
    if "취소" in s:
        return "취소"
    if "종료" in s:
        return "종료"
    if "중단" in s:
        return "중단"
    if "서스펜디드" in s:
        return "서스펜디드"
    if re.search(r"\d+회[초말]", s) or "연장" in s:
        return "진행중"
    if "예정" in s or "경기전" in s or re.match(r"^\d{1,2}:\d{2}$", s):
        return "경기전"
    return s


def make_result(home, away, home_score, away_score):
    if home_score is None or away_score is None:
        return None
    if home_score > away_score:
        return f"{home}승"
    if away_score > home_score:
        return f"{away}승"
    return "무승부"


def build_game_id(date, away, home, time=None, stadium=None):
    return "_".join([
        "" if pd.isna(date) else str(date).strip(),
        "" if pd.isna(away) else str(away).strip(),
        "" if pd.isna(home) else str(home).strip(),
        "" if pd.isna(time) else str(time).strip(),
        "" if pd.isna(stadium) else str(stadium).strip(),
    ])


def _clean_lines(text: str) -> List[str]:
    lines = []
    for line in text.splitlines():
        s = re.sub(r"\s+", " ", line).strip()
        if s:
            lines.append(s)
    return lines


def _is_team_token(s: str) -> bool:
    return normalize_team(s) in TEAM_ALIASES.values()


def _extract_date(text: str) -> Optional[str]:
    # 2026.03.19 / 2026-03-19 / 2026/03/19
    m = re.search(r"(20\d{2})[./-](\d{1,2})[./-](\d{1,2})", text)
    if not m:
        return None
    y, mm, dd = m.group(1), int(m.group(2)), int(m.group(3))
    return f"{y}-{mm:02d}-{dd:02d}"


def _extract_game_rows_from_text(text: str, fallback_date: Optional[str] = None) -> List[Dict]:
    """
    네이버 body inner_text 기준 느슨한 파서.
    핵심 전략:
    - 시간 줄(예: 13:00) 또는 '13:00 사직' 줄을 앵커로 본다.
    - 그 이후 몇 줄 안에서 팀/점수/상태를 모은다.
    """
    lines = _clean_lines(text)
    rows: List[Dict] = []
    season_type = None
    page_date = _extract_date(text) or fallback_date

    time_re = re.compile(r"^(\d{1,2}:\d{2})(?:\s+([가-힣A-Za-z0-9]+))?$")
    team_score_spaced_re = re.compile(r"^([A-Za-z가-힣]+)\s+(\d+)$")
    team_score_joined_re = re.compile(r"^([A-Za-z가-힣]+)(\d+)$")
    simple_team_re = re.compile(r"^([A-Za-z가-힣]+)$")

    i = 0
    while i < len(lines):
        line = lines[i]

        if "시범경기" in line:
            season_type = "시범경기"
        elif "정규시즌" in line:
            season_type = "정규시즌"
        elif "포스트시즌" in line:
            season_type = "포스트시즌"

        m = time_re.match(line)
        if not m:
            i += 1
            continue

        game_time = m.group(1)
        stadium = m.group(2)

        team_candidates = []
        raw_status = None
        inning_text = None

        # 현재 시간 앵커 뒤 최대 8줄 정도 본다.
        j = i + 1
        stop_at_next_time = False
        lookahead = []
        while j < len(lines) and j <= i + 8:
            if time_re.match(lines[j]):
                stop_at_next_time = True
                break
            lookahead.append(lines[j])
            j += 1

        for s in lookahead:
            if "시범경기" in s or "정규시즌" in s or "포스트시즌" in s:
                continue

            if any(tok in s for tok in ["종료", "취소", "우천취소", "경기전", "중단", "서스펜디드", "회초", "회말", "연장"]):
                raw_status = s
                if re.search(r"\d+회[초말]", s) or "연장" in s:
                    inning_text = s
                continue

            m1 = team_score_spaced_re.match(s)
            if m1:
                team_candidates.append((normalize_team(m1.group(1)), safe_int(m1.group(2))))
                continue

            m2 = team_score_joined_re.match(s)
            if m2:
                team_candidates.append((normalize_team(m2.group(1)), safe_int(m2.group(2))))
                continue

            m3 = simple_team_re.match(s)
            if m3 and _is_team_token(normalize_team(m3.group(1))):
                team_candidates.append((normalize_team(m3.group(1)), None))
                continue

        if len(team_candidates) >= 2:
            away, away_score = team_candidates[0]
            home, home_score = team_candidates[1]
            status = normalize_status(raw_status)
            row = {
                "date": page_date,
                "time": game_time,
                "stadium": stadium,
                "away": away,
                "home": home,
                "away_score": away_score,
                "home_score": home_score,
                "status": status,
                "inning_text": inning_text if inning_text else (raw_status or status),
                "result": make_result(home, away, home_score, away_score) if status == "종료" else None,
                "season_type": season_type,
                "game_id": build_game_id(page_date, away, home, game_time, stadium),
            }
            rows.append(row)

        i = j if stop_at_next_time else i + 1

    # 중복 제거
    dedup = []
    seen = set()
    for r in rows:
        k = r["game_id"]
        if k not in seen:
            seen.add(k)
            dedup.append(r)
    return dedup


def parse_scores(
    score_txt_path: str = "debug_artifacts/score_page.txt",
    games_csv_path: str = "data/games.csv",
    live_score_csv_path: str = "data/live_score.csv",
    fallback_date: Optional[str] = None,
):
    text = Path(score_txt_path).read_text(encoding="utf-8")
    rows = _extract_game_rows_from_text(text, fallback_date=fallback_date)
    live_df = pd.DataFrame(rows)

    if live_df.empty:
        live_df = pd.DataFrame(columns=[
            "date", "time", "stadium", "away", "home",
            "away_score", "home_score", "status", "inning_text",
            "result", "season_type", "game_id"
        ])

    # 저장용 컬럼 순서
    live_cols = [
        "date", "time", "stadium", "status", "away", "home",
        "away_score", "home_score", "inning_text", "season_type", "game_id"
    ]
    games_cols = [
        "date", "time", "stadium", "status", "away", "home",
        "away_score", "home_score", "result", "season_type", "game_id"
    ]

    for col in live_cols:
        if col not in live_df.columns:
            live_df[col] = None
    live_df = live_df[live_cols]

    games_df = live_df[live_df["status"] == "종료"].copy()
    if "result" not in games_df.columns:
        games_df["result"] = None
    # result 재계산 보정
    games_df["result"] = games_df.apply(
        lambda r: make_result(r["home"], r["away"], safe_int(r["home_score"]), safe_int(r["away_score"])),
        axis=1
    )
    games_df = games_df[games_cols]

    Path(games_csv_path).parent.mkdir(parents=True, exist_ok=True)
    live_df.to_csv(live_score_csv_path, index=False, encoding="utf-8-sig")
    games_df.to_csv(games_csv_path, index=False, encoding="utf-8-sig")
    return live_df, games_df


def merge_schedule_with_scores(
    schedule_csv_path: str = "data/schedule.csv",
    games_csv_path: str = "data/games.csv",
    output_csv_path: str = "data/schedule.csv",
):
    """
    기존 schedule.csv 에 점수를 덧붙여 같은 파일로 덮어쓰기.
    사용자가 '파일 많이 만들지 말자'고 했으니 기본값을 schedule.csv 자체로 둠.
    """
    schedule = pd.read_csv(schedule_csv_path)
    games = pd.read_csv(games_csv_path)

    for df in (schedule, games):
        for col in ["date", "time", "stadium", "away", "home"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        if "away" in df.columns:
            df["away"] = df["away"].map(normalize_team)
        if "home" in df.columns:
            df["home"] = df["home"].map(normalize_team)

    keep_cols = ["date", "time", "stadium", "away", "home", "away_score", "home_score", "result", "status"]
    games = games[keep_cols].drop_duplicates(subset=["date", "away", "home", "time", "stadium"])

    merged = schedule.merge(
        games,
        on=["date", "time", "stadium", "away", "home"],
        how="left",
        suffixes=("", "_score"),
    )

    if "status_score" in merged.columns:
        merged["status"] = merged["status_score"].combine_first(merged.get("status"))
        merged.drop(columns=["status_score"], inplace=True)

    # schedule.csv가 기존에 away_score/home_score/result를 가지고 있을 수 있으므로 보정
    if "away_score_score" in merged.columns:
        merged["away_score"] = merged["away_score_score"].combine_first(merged.get("away_score"))
        merged.drop(columns=["away_score_score"], inplace=True)
    if "home_score_score" in merged.columns:
        merged["home_score"] = merged["home_score_score"].combine_first(merged.get("home_score"))
        merged.drop(columns=["home_score_score"], inplace=True)
    if "result_score" in merged.columns:
        merged["result"] = merged["result_score"].combine_first(merged.get("result"))
        merged.drop(columns=["result_score"], inplace=True)

    merged.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    return merged


if __name__ == "__main__":
    live_df, games_df = parse_scores()
    print("----- data/live_score.csv -----")
    print(f"rows = {len(live_df)}")
    print(live_df.head())
    print("----- data/games.csv -----")
    print(f"rows = {len(games_df)}")
    print(games_df.head())
