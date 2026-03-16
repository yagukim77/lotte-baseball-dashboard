import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

url = "https://sports.news.naver.com/team/index?teamCode=LT"

res = requests.get(url)

soup = BeautifulSoup(res.text,"lxml")

players = soup.select("td.name")

data = []

for p in players:

    data.append({
        "player": p.text.strip(),
        "ops": round(0.6,2)
    })

df = pd.DataFrame(data)

os.makedirs("data", exist_ok=True)

df.to_csv("data/players_stats.csv", index=False)

print("선수 데이터 저장")
