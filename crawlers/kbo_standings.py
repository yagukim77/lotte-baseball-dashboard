import pandas as pd

teams = [

{"team":"KIA","win":50,"lose":30},
{"team":"LG","win":48,"lose":32},
{"team":"두산","win":45,"lose":35},
{"team":"롯데","win":42,"lose":38},
{"team":"KT","win":40,"lose":40}

]

df = pd.DataFrame(teams)

df["win_rate"] = df["win"] / (df["win"] + df["lose"])

df.to_csv("data/kbo_standings.csv", index=False)

print("KBO 순위 저장")
