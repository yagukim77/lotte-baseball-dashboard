import feedparser
import pandas as pd

url="https://www.youtube.com/feeds/videos.xml?channel_id=UC7c-7z9ZfQkZk5A5n3z0K9Q"

feed=feedparser.parse(url)

videos=[]

for e in feed.entries:

    videos.append({
        "title":e.title,
        "link":e.link
    })

pd.DataFrame(videos).to_csv("data/youtube.csv",index=False)
