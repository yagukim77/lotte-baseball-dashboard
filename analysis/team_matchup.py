def team_record(df):

    result = df.groupby("opponent").sum()

    result["win_rate"] = result["win"]/(result["win"]+result["lose"])

    return result