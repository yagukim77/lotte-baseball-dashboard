import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote

keyword = "롯데자이언츠"

google_url = f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"

naver_url = f"https://news.google.com/rss/search?q=site:naver.com+{quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"

urls = [google_url, naver_url]

news = []

for url in urls:

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "xml")

    items = soup.find_all("item")

    for i in items:

        title = i.title.text
        link = i.link.text
        pubdate = i.pubDate.text

        news.append({
            "title": title,
            "link": link,
            "date": pubdate
        })

df = pd.DataFrame(news)

# 중복 제거
df = df.drop_duplicates(subset="title")

df.to_csv("news.csv", index=False)

print("뉴스 수집:", len(df))
