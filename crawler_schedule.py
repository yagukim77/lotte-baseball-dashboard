import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://sports.news.naver.com/kbaseball/schedule/index"

headers = {"User-Agent":"Mozilla/5.0"}

res = requests.get(url,headers=headers)

soup = BeautifulSoup(res.text,"lxml")

games=[]
rows=soup.select("table tbody tr")

for r in rows:

    try:
        date=r.select_one(".td_date").text.strip()
        teams=r.select_one(".td_vs").text.strip()
        stadium=r.select_one(".td_stadium").text.strip()

        games.append({
            "date":date,
            "match":teams,
            "stadium":stadium
        })
    except:
        pass

df=pd.DataFrame(games)

df.to_csv("schedule.csv",index=False)

print("경기 일정 저장 완료")