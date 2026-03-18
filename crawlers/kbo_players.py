import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"

def crawl_players():

    r = requests.get(URL)
    soup = BeautifulSoup(r.text,"html.parser")

    table = soup.select_one("table.tData")

    rows = table.select("tbody tr")

    data=[]

    for r in rows:

        c=[x.text.strip() for x in r.select("td")]

        player=c[1]
        team=c[2]
        avg=c[3]
        hr=c[8]
        rbi=c[9]
        ops=c[-1]

        data.append({
            "player":player,
            "team":team,
            "avg":avg,
            "hr":hr,
            "rbi":rbi,
            "ops":ops
        })

    df=pd.DataFrame(data)

    df.to_csv("data/players_stats.csv",index=False)