import pandas as pd
import re

# =========================
# 공통 텍스트 로드
# =========================
def load_txt(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


# =========================
# 타자 파싱
# =========================
def parse_hitters():
    lines = load_txt("debug_artifacts/naver_kbo_record_hitter.txt")

    players = []
    i = 0

    while i < len(lines):
        if lines[i].strip() == "타율":
            try:
                name = lines[i-2].strip()
                team = lines[i-1].strip()

                avg = float(lines[i+1])
                ops_idx = lines.index("OPS", i)
                ops = float(lines[ops_idx+1])

                players.append({
                    "player": name,
                    "team": team,
                    "avg": avg,
                    "ops": ops
                })

                i = ops_idx
            except:
                pass
        i += 1

    df = pd.DataFrame(players)
    df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")
    print("hitters OK")


# =========================
# 투수 파싱
# =========================
def parse_pitchers():
    lines = load_txt("debug_artifacts/naver_kbo_record_pitcher.txt")

    players = []
    i = 0

    while i < len(lines):
        if lines[i].strip() == "평균자책":
            try:
                name = lines[i-2].strip()
                team = lines[i-1].strip()

                era = float(lines[i+1])
                game = int(lines[i+3])
                win = int(lines[i+5])
                lose = int(lines[i+7])

                players.append({
                    "player": name,
                    "team": team,
                    "era": era,
                    "game": game,
                    "win": win,
                    "lose": lose
                })
            except:
                pass
        i += 1

    df = pd.DataFrame(players)
    df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")
    print("pitchers OK")


# =========================
# 일정 파싱
# =========================
def parse_schedule():
    lines = load_txt("debug_artifacts/naver_kbo_schedule.txt")

    games = []
    i = 0

    while i < len(lines):
        if lines[i] == "경기 시간":
            try:
                time = lines[i+1]
                stadium = lines[i+3]
                status = lines[i+4]

                away = lines[i+5]
                home = lines[i+6]

                games.append({
                    "time": time,
                    "stadium": stadium,
                    "status": status,
                    "away": away,
                    "home": home
                })
            except:
                pass
        i += 1

    df = pd.DataFrame(games)
    df.to_csv("data/schedule.csv", index=False, encoding="utf-8-sig")
    print("schedule OK")


# =========================
# 실행
# =========================
if __name__ == "__main__":
    parse_hitters()
    parse_pitchers()
    parse_schedule()
