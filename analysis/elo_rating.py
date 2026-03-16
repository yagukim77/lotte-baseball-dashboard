import pandas as pd

def calculate_elo():

    try:
        df = pd.read_csv("data/games.csv")
    except:
        return 1500

    rating = 1500

    for _,row in df.iterrows():

        if row["result"] == "W":
            rating += 10
        else:
            rating -= 10

    return rating
