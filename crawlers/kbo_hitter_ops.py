import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"

def crawl_hitter_ops():

    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one("table.tData")

    rows = table.select("tbody tr")

    data = []

    for r in rows:

        cols = [c.text.strip() for c in r.select("td")]

        player = cols[1]
        team = cols[2]
        avg = cols[3]
        hr = cols[8]
        rbi = cols[9]
        ops = cols[-1]

        data.append({
            "player": player,
            "team": team,
            "avg": avg,
            "hr": hr,
            "rbi": rbi,
            "ops": ops
        })

    df = pd.DataFrame(data)

    df.to_csv("data/kbo_hitters.csv", index=False)

    print("OPS data saved")

if __name__ == "__main__":
    crawl_hitter_ops()
