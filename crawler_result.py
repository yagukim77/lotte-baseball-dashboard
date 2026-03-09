import requests
import pandas as pd
from bs4 import BeautifulSoup

url="https://sports.news.naver.com/kbaseball/scoreboard/index"

headers={"User-Agent":"Mozilla/5.0"}

res=requests.get(url,headers=headers)

soup=BeautifulSoup(res.text,"lxml")

games=[]

rows=soup.select(".sch_tb tbody tr")

for r in rows:

    try:

        teams=r.select_one(".team_lft").text.strip()+" vs "+r.select_one(".team_rgt").text.strip()

        score=r.select_one(".td_score").text.strip()

        games.append({
            "match":teams,
            "score":score
        })

    except:
        pass

df=pd.DataFrame(games)

df.to_csv("result.csv",index=False)

print("경기 결과 저장")