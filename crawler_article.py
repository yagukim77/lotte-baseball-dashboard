import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv("data/news.csv")

articles = []

for _, r in df.iterrows():

    try:

        res = requests.get(r["link"], timeout=5)

        soup = BeautifulSoup(res.text,"lxml")

        text = soup.get_text()

        articles.append({
            "title": r["title"],
            "text": text
        })

    except:

        articles.append({
            "title": r["title"],
            "text": ""
        })

pd.DataFrame(articles).to_csv("data/articles.csv", index=False)

print("기사 수집 완료")
