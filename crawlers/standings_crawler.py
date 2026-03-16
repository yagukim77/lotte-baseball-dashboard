import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

url = "https://sports.news.naver.com/kbaseball/record/index"

res = requests.get(url)
soup = BeautifulSoup(res.text, "lxml")

teams = soup.select("span.name")
wins = soup.select("td.win")
loss = soup.select("td.lose")

data = []

for i in range(len(teams)):

    data.append({
        "team": teams[i].text,
        "win": wins[i].text,
        "lose": loss[i].text
    })

df = pd.DataFrame(data)

os.makedirs("data", exist_ok=True)

df.to_csv("data/kbo_standings.csv", index=False)

print("KBO 순위 저장")
