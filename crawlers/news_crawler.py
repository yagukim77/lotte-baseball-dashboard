import feedparser
import pandas as pd

query = "롯데자이언츠"

urls = [

f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko",

f"https://rss.naver.com/search.naver?query={query}"

]

news = []

for url in urls:

    feed = feedparser.parse(url)

    for entry in feed.entries:

        news.append({

        "title": entry.title,

        "link": entry.link,

        "summary": entry.get("summary","")

        })

df = pd.DataFrame(news)

df.to_csv("data/news.csv",index=False)

print("뉴스 저장:",len(df))
