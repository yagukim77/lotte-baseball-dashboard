import feedparser
import pandas as pd
from datetime import datetime

query = "롯데 자이언츠"

google_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
naver_url = f"https://rss.naver.com/search.naver?query={query}"

feeds = [google_url, naver_url]

rows = []

for url in feeds:

    feed = feedparser.parse(url)

    for e in feed.entries:

        rows.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "title": e.title,
            "link": e.link
        })

df = pd.DataFrame(rows)

df = df.drop_duplicates(subset=["title"])

df.to_csv("data/news.csv", index=False)

print("뉴스 저장:", len(df))
