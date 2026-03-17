import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"

def crawl_schedule():

    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    games = soup.select(".game-cont")

    data = []

    for g in games:

        teams = g.select(".team-name")

        if len(teams) < 2:
            continue

        away = teams[0].text.strip()
        home = teams[1].text.strip()

        data.append({
            "away": away,
            "home": home
        })

    df = pd.DataFrame(data)

    df.to_csv("data/kbo_schedule.csv", index=False)

    print("schedule saved")

if __name__ == "__main__":
    crawl_schedule()
