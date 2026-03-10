import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://sports.news.naver.com/kbaseball/index"

headers = {
"User-Agent":"Mozilla/5.0"
}

res = requests.get(url, headers=headers)

soup = BeautifulSoup(res.text,"lxml")

games = []

rows = soup.select(".home_game_list li")

for r in rows:

    try:

        team1 = r.select_one(".team_lft").text.strip()
        team2 = r.select_one(".team_rgt").text.strip()

        score = r.select_one(".score").text.strip()

        games.append({
            "match":f"{team1} vs {team2}",
            "score":score
        })

    except:
        pass

df = pd.DataFrame(games)

df.to_csv("score.csv", index=False)

print("경기 스코어 저장")
