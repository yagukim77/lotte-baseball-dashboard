import pandas as pd
import os

games = [
("2026-03-20","롯데","LG"),
("2026-03-21","롯데","LG"),
("2026-03-22","롯데","LG"),
("2026-03-23","롯데","NC"),
("2026-03-24","롯데","NC")
]

df = pd.DataFrame(
    games,
    columns=["date","team","opponent"]
)

os.makedirs("data",exist_ok=True)

df.to_csv("data/schedule.csv",index=False)

print("schedule updated")