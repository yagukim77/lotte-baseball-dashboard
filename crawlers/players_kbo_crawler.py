import pandas as pd

players = [
("전준우",0.812),
("고승민",0.789),
("윤동희",0.770),
("레이예스",0.845),
("유강남",0.720),
("박승욱",0.700)
]

df = pd.DataFrame(players,columns=["name","ops"])

df.to_csv("data/players_stats.csv",index=False)