import pandas as pd
import datetime

today = datetime.date.today()

if today.month < 4:
    url = "https://www.koreabaseball.com/Record/CampRank/CampRank.aspx"
else:
    url = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"

tables = pd.read_html(url)

df = tables[0]

df.to_csv("data/kbo_standings.csv",index=False)