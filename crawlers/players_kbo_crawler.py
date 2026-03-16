import pandas as pd

url = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"

tables = pd.read_html(url)

df = tables[0]

df = df[["선수명","OPS"]]

df.columns = ["name","ops"]

df.to_csv("data/players_stats.csv",index=False)

print("players updated")
