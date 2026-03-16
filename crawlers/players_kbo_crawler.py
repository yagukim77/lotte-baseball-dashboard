import pandas as pd

players = [

{"name":"전준우","ops":0.820},
{"name":"한동희","ops":0.780},
{"name":"레이예스","ops":0.720},
{"name":"유강남","ops":0.690},
{"name":"고승민","ops":0.760}

]

df = pd.DataFrame(players)

df.to_csv("data/players_stats.csv",index=False)

print("선수 기록 저장")
