import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime


def get_season_type():

    month = datetime.now().month

    if month <= 3:
        return "preseason"

    elif month <= 9:
        return "regular"

    else:
        return "postseason"


def crawl_standings():

    season = get_season_type()

    if season == "preseason":

        url = "https://sports.news.naver.com/kbaseball/record/index?category=kbo&type=prematch"

    else:

        url = "https://sports.news.naver.com/kbaseball/record/index?category=kbo"

    res = requests.get(url)

    soup = BeautifulSoup(res.text,"lxml")

    rows = soup.select("table tbody tr")

    data = []

    for r in rows:

        cols = r.find_all("td")

        if len(cols) < 5:
            continue

        team = cols[0].text.strip()
        win = cols[1].text.strip()
        lose = cols[2].text.strip()
        draw = cols[3].text.strip()

        data.append({
            "team":team,
            "win":win,
            "lose":lose,
            "draw":draw
        })

    df = pd.DataFrame(data)

    os.makedirs("data",exist_ok=True)

    df.to_csv("data/kbo_standings.csv",index=False)

    print("standings updated")


crawl_standings()
