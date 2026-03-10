import pandas as pd

url = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"

df = pd.read_html(url)[0]

lotte = df[df["팀명"] == "롯데"]

lotte.to_csv("players_stats.csv", index=False)
