import pandas as pd
import datetime
import os

today = datetime.date.today()

data = [
    {
        "date": today,
        "home": "롯데",
        "away": "두산",
        "stadium": "사직"
    }
]

df = pd.DataFrame(data)

os.makedirs("data", exist_ok=True)

df.to_csv("data/schedule.csv", index=False)

print("경기 일정 저장")
