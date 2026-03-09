import feedparser
import pandas as pd
from datetime import datetime

url = "https://news.google.com/rss/search?q=롯데자이언츠&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(url)

data = []

for entry in feed.entries:

    date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")

    data.append({
        "date": date,
        "title": entry.title,
        "link": entry.link
    })

df = pd.DataFrame(data)

df = df.drop_duplicates(subset=["title"])

df.to_csv("news.csv", index=False)

print("뉴스 저장:", len(df))