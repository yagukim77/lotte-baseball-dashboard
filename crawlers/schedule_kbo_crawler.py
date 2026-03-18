import pandas as pd
from datetime import date

games = [

{"date":"2026-04-01","opponent":"두산"},
{"date":"2026-04-02","opponent":"LG"},
{"date":"2026-04-03","opponent":"SSG"}

]

df = pd.DataFrame(games)

df.to_csv("data/schedule.csv",index=False)