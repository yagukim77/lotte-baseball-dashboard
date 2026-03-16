import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url_list = [
    # 시범경기
    "https://sports.news.naver.com/kbaseball/record/index?category=kbo&year=2026&type=prematch",
    
    # 정규시즌
    "https://sports.news.naver.com/kbaseball/record/index?category=kbo"
]

data = []

for url in url_list:

    try:

        res = requests.get(url)
        soup = BeautifulSoup(res.text,"lxml")

        table = soup.select("table tbody tr")

        if len(table) == 0:
            continue

        for row in table:

            cols = row.find_all("td")

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

        break

    except:
        continue

df = pd.DataFrame(data)

os.makedirs("data",exist_ok=True)

df.to_csv("data/kbo_standings.csv",index=False)

print("KBO 순위 저장 완료")
