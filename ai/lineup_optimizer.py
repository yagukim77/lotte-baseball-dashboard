def recommend_lineup(df):

    df=df.sort_values("ops",ascending=False)

    return df["name"].tolist()[:9]