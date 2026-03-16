import feedparser
import pandas as pd
import os

url = "https://news.google.com/rss/search?q=롯데자이언츠&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(url)

data = []

for entry in feed.entries:

    data.append({
        "title":entry.title,
        "link":entry.link
    })

df = pd.DataFrame(data)

os.makedirs("data",exist_ok=True)

df.to_csv("data/news.csv",index=False)

print("뉴스 저장 완료")
