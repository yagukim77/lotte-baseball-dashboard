import pandas as pd

def analyze_recent_games():

    df = pd.read_csv("data/games.csv")

    last10 = df.tail(10)

    wins = len(last10[last10["result"]=="W"])
    loses = len(last10[last10["result"]=="L"])

    return wins, loses
