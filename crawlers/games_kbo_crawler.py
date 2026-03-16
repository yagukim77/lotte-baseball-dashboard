import pandas as pd

games = [

{"date":"2026-03-10","opponent":"LG","win":5,"lose":3,"result":"W"},
{"date":"2026-03-11","opponent":"KT","win":4,"lose":7,"result":"L"},
{"date":"2026-03-12","opponent":"KIA","win":6,"lose":2,"result":"W"}

]

df = pd.DataFrame(games)

df.to_csv("data/games.csv",index=False)
