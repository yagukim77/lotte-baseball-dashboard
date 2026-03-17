import numpy as np

def simulate_game(a_attack,b_attack,n=1000):

    aw=0
    bw=0

    scores=[]

    for i in range(n):

        sa = np.random.poisson(a_attack)
        sb = np.random.poisson(b_attack)

        scores.append((sa,sb))

        if sa>sb:
            aw+=1
        elif sb>sa:
            bw+=1

    return {
        "A_win":aw/n,
        "B_win":bw/n,
        "A_score":np.mean([s[0] for s in scores]),
        "B_score":np.mean([s[1] for s in scores])
    }
