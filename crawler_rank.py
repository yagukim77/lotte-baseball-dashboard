import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://sports.news.naver.com/kbaseball/record/index"

headers = {"User-Agent":"Mozilla/5.0"}

res = requests.get(url,headers=headers)

soup = BeautifulSoup(res.text,"lxml")

teams=[]
wins=[]
loss=[]

rows=soup.select("table tbody tr")

for r in rows[:10]:

    t=r.select_one(".tm").text
    w=r.select("td")[3].text
    l=r.select("td")[4].text

    teams.append(t)
    wins.append(w)
    loss.append(l)

df=pd.DataFrame({
"team":teams,
"win":wins,
"loss":loss
})

df.to_csv("rank.csv",index=False)

print("순위 저장 완료")