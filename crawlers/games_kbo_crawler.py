import pandas as pd

games = [

("2026-03-10","LG",1,0,"승"),
("2026-03-11","LG",0,1,"패"),
("2026-03-12","KT",1,0,"승"),
("2026-03-13","KT",1,0,"승")

]

df = pd.DataFrame(games,columns=["date","opponent","win","lose","result"])

df.to_csv("data/games.csv",index=False)