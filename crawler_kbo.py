import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://sports.news.naver.com/kbaseball/record/index"

res = requests.get(url)

soup = BeautifulSoup(res.text,"lxml")

rows = soup.select("table tbody tr")

teams=[]

for r in rows:

    cols = r.find_all("td")

    if len(cols) < 7:
        continue

    teams.append({
        "team":cols[1].text,
        "win":cols[3].text,
        "lose":cols[4].text,
        "rate":cols[6].text
    })

df = pd.DataFrame(teams)

df.to_csv("data/kbo_rank.csv",index=False)
