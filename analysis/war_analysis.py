def calculate_war(df):

    df["WAR"] = df["ops"] * 10

    return df