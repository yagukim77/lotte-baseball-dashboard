import pandas as pd

def recent_performance():

    try:
        df = pd.read_csv("data/games.csv")
    except:
        return 0.5

    last10 = df.tail(10)

    wins = len(last10[last10["result"]=="W"])

    games = len(last10)

    if games == 0:
        return 0.5

    return wins/games


def predict_win():

    perf = recent_performance()

    base = 0.5

    prob = base + (perf-0.5)*0.7

    if prob > 0.8:
        prob = 0.8

    if prob < 0.2:
        prob = 0.2

    return round(prob,2)


def predict_score():

    p = predict_win()

    if p > 0.6:
        return "롯데 6 : 3 상대팀"

    if p > 0.5:
        return "롯데 5 : 4 상대팀"

    return "롯데 3 : 5 상대팀"
