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

    return round(wins/games,2)


def predict_win():

    perf = recent_performance()

    base = 0.5

    prob = base + (perf-0.5)*0.6

    return round(prob,2)


def predict_score():

    win_prob = predict_win()

    if win_prob > 0.6:
        return "롯데 6 : 3 상대팀"

    elif win_prob > 0.5:
        return "롯데 5 : 4 상대팀"

    else:
        return "롯데 3 : 5 상대팀"
