import numpy as np

def simulate_game(team,opp,n=1000):

    win=0

    for i in range(n):

        t=np.random.poisson(team)
        o=np.random.poisson(opp)

        if t>o:
            win+=1

    return win/n