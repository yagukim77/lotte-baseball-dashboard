import numpy as np

def predict_score(team,opp):

    t=np.random.poisson(team)
    o=np.random.poisson(opp)

    return t,o