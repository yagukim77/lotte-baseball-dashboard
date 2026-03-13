import feedparser
import pandas as pd

url="https://news.google.com/rss/search?q=롯데자이언츠&hl=ko&gl=KR&ceid=KR:ko"

feed=feedparser.parse(url)

data=[]

for entry in feed.entries:

    data.append({
        "title":entry.title,
        "summary":entry.summary,
        "link":entry.link
    })

df=pd.DataFrame(data)

df.to_csv("data/news.csv",index=False)