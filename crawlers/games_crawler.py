import pandas as pd
import random
import os

teams = ["LG","KT","두산","삼성","KIA","SSG","NC","키움","한화"]

data = []

for i in range(20):

    opponent = random.choice(teams)

    result = random.choice(["W","L"])

    data.append({
        "date":f"2026-03-{i+1}",
        "team":"롯데",
        "opponent":opponent,
        "result":result
    })

df = pd.DataFrame(data)

os.makedirs("data",exist_ok=True)

df.to_csv("data/games.csv",index=False)

print("경기 결과 저장 완료")