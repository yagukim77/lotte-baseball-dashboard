import pandas as pd

# 정규시즌 url = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"

url = "https://www.koreabaseball.com/Record/CampRank/CampRank.aspx"

tables = pd.read_html(url)

df = tables[0]

df = df[["팀명","승","패","무","승률"]]

df.columns = ["team","win","lose","draw","rate"]

df.to_csv("data/kbo_standings.csv",index=False)

print("KBO standings saved")
