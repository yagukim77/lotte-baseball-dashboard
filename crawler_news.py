import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote

keyword = "롯데 자이언츠"

google = f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"

naver = f"https://news.google.com/rss/search?q=site:naver.com+{quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"

urls = [google, naver]

news = []

for url in urls:

    res = requests.get(url)

    soup = BeautifulSoup(res.text, "xml")

    items = soup.find_all("item")

    for i in items:

        news.append({
            "title": i.title.text,
            "link": i.link.text,
            "date": i.pubDate.text
        })

df = pd.DataFrame(news)

df = df.drop_duplicates(subset="title")

df.to_csv("news.csv", index=False)

print("뉴스:", len(df))
