import random

def simulate(lotte_ops, opp_ops):

    prob = lotte_ops / (lotte_ops + opp_ops)

    lotte = int(prob * 10) + random.randint(0,2)
    opp = int((1-prob) * 10) + random.randint(0,2)

    if lotte > opp:
        result = "롯데 승리"
    else:
        result = "상대팀 승리"

    return lotte, opp, result
