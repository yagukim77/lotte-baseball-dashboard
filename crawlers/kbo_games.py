import pandas as pd

def crawl_games():

    df=pd.read_csv("data/games_raw.csv")

    df["result"]=df.apply(
        lambda x:"W" if x["runs"]>x["allowed"] else "L",
        axis=1
    )

    df.to_csv("data/games.csv",index=False)