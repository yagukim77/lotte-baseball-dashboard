import pandas as pd

schedule = [

("2026-03-20","LG"),
("2026-03-21","LG"),
("2026-03-22","LG"),
("2026-03-24","두산")

]

df = pd.DataFrame(schedule,columns=["date","opponent"])

df.to_csv("data/schedule.csv",index=False)