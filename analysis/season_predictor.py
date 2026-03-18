import pandas as pd

def predict_season():

    df=pd.read_csv("data/team_stats.csv")

    df["score"]=df["team_ops"]*100

    df=df.sort_values("score",ascending=False)

    df["pred_rank"]=range(1,len(df)+1)

    return df