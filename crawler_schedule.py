import requests
import pandas as pd
from bs4 import BeautifulSoup

url="https://sports.news.naver.com/kbaseball/schedule/index"

res=requests.get(url)

soup=BeautifulSoup(res.text,"lxml")

games=[]

rows=soup.select(".tb_wrap tbody tr")

for r in rows:

    cols=r.find_all("td")

    if len(cols)<3:
        continue

    games.append({
        "date":cols[0].text,
        "match":cols[1].text,
        "stadium":cols[2].text
    })

pd.DataFrame(games).to_csv("data/schedule.csv",index=False)


print("경기 일정 저장 완료")
