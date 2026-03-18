import os
import pandas as pd
from playwright.sync_api import sync_playwright

TEAM_MAP = {
    "롯데": "롯데", "두산": "두산", "NC": "NC", "SSG": "SSG",
    "삼성": "삼성", "LG": "LG", "KIA": "KIA", "한화": "한화",
    "KT": "KT", "키움": "키움"
}

def fetch_data():
    os.makedirs("data", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # =========================
        # 1. 일정 + 결과
        # =========================
        page.goto("https://m.sports.naver.com/kbaseball/schedule/index")

        page.wait_for_timeout(3000)

        games = []

        rows = page.query_selector_all("div.match_list div.match_item")

        for r in rows:
            try:
                teams = r.query_selector_all("span.name")
                if len(teams) < 2:
                    continue

                away = teams[0].inner_text()
                home = teams[1].inner_text()

                score = r.query_selector("span.score")
                status = r.query_selector("span.state")

                away_score = None
                home_score = None

                if score:
                    s = score.inner_text()
                    if ":" in s:
                        a, b = s.split(":")
                        away_score = int(a)
                        home_score = int(b)

                games.append({
                    "date": "",
                    "away": away,
                    "home": home,
                    "away_score": away_score,
                    "home_score": home_score,
                    "status": status.inner_text() if status else ""
                })
            except:
                pass

        schedule_df = pd.DataFrame(games)
        schedule_df.to_csv("data/schedule.csv", index=False, encoding="utf-8-sig")

        # =========================
        # 2. 타자 기록
        # =========================
        page.goto("https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter")
        page.wait_for_timeout(3000)

        hitters = []

        rows = page.query_selector_all("table tbody tr")

        for r in rows:
            try:
                tds = r.query_selector_all("td")
                if len(tds) < 10:
                    continue

                player = tds[1].inner_text()
                team = tds[2].inner_text()
                avg = float(tds[3].inner_text())
                hr = int(tds[6].inner_text())
                rbi = int(tds[7].inner_text())

                ops = avg + (hr * 0.02) + 0.3

                hitters.append({
                    "player": player,
                    "team": team,
                    "avg": avg,
                    "hr": hr,
                    "rbi": rbi,
                    "ops": round(ops, 3)
                })
            except:
                pass

        hitters_df = pd.DataFrame(hitters)
        hitters_df.to_csv("data/players_stats.csv", index=False, encoding="utf-8-sig")

        # =========================
        # 3. 투수 기록
        # =========================
        page.goto("https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher")
        page.wait_for_timeout(3000)

        pitchers = []

        rows = page.query_selector_all("table tbody tr")

        for r in rows:
            try:
                tds = r.query_selector_all("td")
                if len(tds) < 8:
                    continue

                player = tds[1].inner_text()
                team = tds[2].inner_text()
                era = float(tds[3].inner_text())
                game = int(tds[4].inner_text())
                win = int(tds[5].inner_text())
                lose = int(tds[6].inner_text())
                save = int(tds[7].inner_text())

                pitchers.append({
                    "player": player,
                    "team": team,
                    "era": era,
                    "game": game,
                    "win": win,
                    "lose": lose,
                    "save": save
                })
            except:
                pass

        pitchers_df = pd.DataFrame(pitchers)
        pitchers_df.to_csv("data/pitcher_stats.csv", index=False, encoding="utf-8-sig")

        browser.close()

    # =========================
    # 4. games.csv 생성
    # =========================
    if not schedule_df.empty:
        ended = schedule_df[schedule_df["status"].str.contains("종료", na=False)]

        ended["runs"] = ended["home_score"]
        ended["allowed"] = ended["away_score"]

        ended["result"] = ended.apply(
            lambda r: "W" if r["runs"] > r["allowed"] else ("L" if r["runs"] < r["allowed"] else "D"),
            axis=1
        )

        ended[["date", "home", "away", "runs", "allowed", "result"]].to_csv(
            "data/games.csv", index=False, encoding="utf-8-sig"
        )

    # =========================
    # 5. 팀 스탯
    # =========================
    if not hitters_df.empty:
        team_stats = hitters_df.groupby("team").agg(
            avg=("avg", "mean"),
            team_ops=("ops", "mean")
        ).reset_index()

        team_stats.to_csv("data/team_stats.csv", index=False, encoding="utf-8-sig")

    print("ALL DATA UPDATED")


if __name__ == "__main__":
    fetch_data()
