import pandas as pd

def build_team_stats():

    df=pd.read_csv("data/players_stats.csv")

    team=df.groupby("team")["ops"].mean().reset_index()

    team.columns=["team","team_ops"]

    team.to_csv("data/team_stats.csv",index=False)
