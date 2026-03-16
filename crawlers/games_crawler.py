import pandas as pd
import datetime
import os

data = [
    {"date":"2026-03-01","team":"롯데","opponent":"LG","result":"W"},
    {"date":"2026-03-02","team":"롯데","opponent":"NC","result":"L"},
    {"date":"2026-03-03","team":"롯데","opponent":"삼성","result":"W"}
]

df = pd.DataFrame(data)

os.makedirs("data", exist_ok=True)

df.to_csv("data/games.csv", index=False)

print("경기 결과 저장")
