def elo(team,opp):

    base = 1500

    diff = team - opp

    rating = base + diff*100

    return rating