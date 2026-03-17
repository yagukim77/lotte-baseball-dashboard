import pandas as pd

def team_attack_power(team):

    df = pd.read_csv("data/players_stats.csv")

    team_df = df[df["team"] == team]

    if len(team_df) == 0:
        return 4.5

    ops = team_df["ops"].astype(float).mean()

    attack = ops * 5

    return round(attack,2)


def recent_form():

    df = pd.read_csv("data/games.csv")

    last10 = df.tail(10)

    wins = len(last10[last10["result"]=="W"])
    loses = len(last10[last10["result"]=="L"])

    avg_score = last10["runs"].mean()
    avg_allowed = last10["allowed"].mean()

    return wins,loses,avg_score,avg_allowed
