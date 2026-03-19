import os
import re
import pandas as pd

DEBUG_DIR = "debug_artifacts"
DATA_DIR = "data"
TEAM_SET = {"LG", "KIA", "NC", "SSG", "삼성", "한화", "KT", "키움", "두산", "롯데"}

def ensure_outfiles():
    os.makedirs(DATA_DIR, exist_ok=True)
    schema = {
        "players_stats.csv": ["player", "team", "avg", "hr", "rbi", "ops"],
        "pitcher_stats.csv": ["player", "team", "era", "game", "win", "lose", "save"],
        "schedule.csv": ["date", "time", "stadium", "status", "away", "home", "away_score", "home_score", "result", "season_type"],
        "games.csv": ["date", "home", "away", "runs", "allowed", "result"],
        "team_stats.csv": ["team", "avg", "era", "team_ops"],
    }
    for name, cols in schema.items():
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            pd.DataFrame(columns=cols).to_csv(path, index=False, encoding="utf-8-sig")

def load_lines(name):
    path = os.path.join(DEBUG_DIR, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [x.strip() for x in f.read().splitlines() if x.strip()]

def write_csv(name, df, cols):
    path = os.path.join(DATA_DIR, name)
    if df is None or df.empty:
        pd.DataFrame(columns=cols).to_csv(path, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(path, index=False, encoding="utf-8-sig")

def valid_player_team(name, team):
    if name in ["위", "-", "더보기", "승", "패", "세이브", "평균자책", "타율"]:
        return False
    if team not in TEAM_SET:
        return False
    if re.fullmatch(r"\d+승", name):
        return False
    if len(name) < 2:
        return False
    return True

def parse_hitters():
    lines = load_lines("hitter.txt")
    rows = []
    i = 0
    while i < len(lines):
        if lines[i] == "타율":
            try:
                name = lines[i-2]
                team = lines[i-1]
                if not valid_player_team(name, team):
                    i += 1
                    continue
                avg = float(lines[i+1])
                hr, rbi, ops = 0, 0, None
                for j in range(i, min(i+60, len(lines)-1)):
                    if lines[j] == "홈런":
                        hr = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                    elif lines[j] == "타점":
                        rbi = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                    elif lines[j] == "OPS":
                        ops = float(lines[j+1])
                        break
                if ops is not None:
                    rows.append({
                        "player": name,
                        "team": team,
                        "avg": avg,
                        "hr": hr,
                        "rbi": rbi,
                        "ops": ops,
                    })
                    i += 20
                    continue
            except Exception:
                pass
        i += 1
    df = pd.DataFrame(rows).drop_duplicates(subset=["player", "team"])
    write_csv("players_stats.csv", df, ["player", "team", "avg", "hr", "rbi", "ops"])
    return df

def parse_pitchers():
    lines = load_lines("pitcher.txt")
    rows = []
    i = 0
    while i < len(lines):
        if lines[i] == "평균자책":
            try:
                name = lines[i-2]
                team = lines[i-1]
                if not valid_player_team(name, team):
                    i += 1
                    continue
                era = float(lines[i+1])
                game = win = lose = save = 0
                for j in range(i, min(i+50, len(lines)-1)):
                    if lines[j] == "경기":
                        game = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                    elif lines[j] == "승":
                        win = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                    elif lines[j] == "패":
                        lose = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                    elif lines[j] == "세이브":
                        save = int(re.sub(r"[^\d]", "", lines[j+1]) or 0)
                        break
                rows.append({
                    "player": name,
                    "team": team,
                    "era": era,
                    "game": game,
                    "win": win,
                    "lose": lose,
                    "save": save,
                })
                i += 20
                continue
            except Exception:
                pass
        i += 1
    df = pd.DataFrame(rows).drop_duplicates(subset=["player", "team"])
    write_csv("pitcher_stats.csv", df, ["player", "team", "era", "game", "win", "lose", "save"])
    return df

def parse_schedule():
    lines = load_lines("schedule.txt")
    rows = []
    i = 0
    while i < len(lines):
        if lines[i] == "경기 시간":
            try:
                game_time = lines[i+1]
                stadium = lines[i+3]
                status = lines[i+4]

                # 네이버 일정 텍스트 구조:
                # 경기 시간 / 13:00 / 경기장 / 사직 / 예정(or 종료) / 두산 / 롯데 / 홈 / ...
                # 종료 상태일 때 승/패가 팀 뒤에 붙어 나와서 홈팀은 +1 오프셋 필요
                away = lines[i+5]

                if i + 7 < len(lines) and lines[i+7] == "홈":
                    home = lines[i+6]
                    step = 8
                elif i + 8 < len(lines) and lines[i+8] == "홈":
                    # 종료 상태 + 승/패 끼어드는 경우
                    home = lines[i+6]
                    if lines[i+7] in {"승", "패", "무"}:
                        step = 9
                    else:
                        home = lines[i+7]
                        step = 9
                else:
                    # 가장 안전한 fallback
                    possible = [x for x in lines[i+6:i+10] if x in TEAM_SET]
                    home = possible[0] if possible else ""
                    step = 10

                if away not in TEAM_SET or home not in TEAM_SET:
                    i += 1
                    continue

                rows.append({
                    "date": "",
                    "time": game_time,
                    "stadium": stadium,
                    "status": status,
                    "away": away,
                    "home": home,
                    "away_score": None,
                    "home_score": None,
                    "result": "",
                    "season_type": "시범경기",
                })
                i += step
                continue
            except Exception:
                pass
        i += 1
    df = pd.DataFrame(rows).drop_duplicates(subset=["away", "home", "time", "stadium", "status"])
    write_csv("schedule.csv", df, ["date", "time", "stadium", "status", "away", "home", "away_score", "home_score", "result", "season_type"])
    return df

def build_games(schedule_df):
    cols = ["date", "home", "away", "runs", "allowed", "result"]
    try:
        if schedule_df is None or schedule_df.empty:
            write_csv("games.csv", pd.DataFrame(columns=cols), cols)
            return

        # 현재 일정 텍스트에서는 점수가 안정적으로 안 잡히므로, 종료 경기라도 games.csv는 비워두는 게 맞음
        # 잘못된 승/패/0점 데이터를 만드는 것보다 안전함
        out = pd.DataFrame(columns=cols)
        write_csv("games.csv", out, cols)
    except Exception:
        write_csv("games.csv", pd.DataFrame(columns=cols), cols)

def build_team_stats(players_df, pitchers_df):
    cols = ["team", "avg", "era", "team_ops"]
    try:
        out = pd.DataFrame()
        if players_df is not None and not players_df.empty and {"team","avg","ops"}.issubset(players_df.columns):
            hit = players_df.groupby("team", as_index=False).agg(avg=("avg","mean"), team_ops=("ops","mean"))
            out = hit
        if pitchers_df is not None and not pitchers_df.empty and {"team","era"}.issubset(pitchers_df.columns):
            pit = pitchers_df.groupby("team", as_index=False).agg(era=("era","mean"))
            out = pit if out.empty else out.merge(pit, on="team", how="outer")
        write_csv("team_stats.csv", out, cols)
    except Exception:
        write_csv("team_stats.csv", pd.DataFrame(columns=cols), cols)

if __name__ == "__main__":
    ensure_outfiles()
    hitters = parse_hitters()
    pitchers = parse_pitchers()
    schedule = parse_schedule()
    build_games(schedule)
    build_team_stats(hitters, pitchers)
