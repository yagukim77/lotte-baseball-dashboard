import random

def simulate_game(lotte_ops, opp_ops):

    base = lotte_ops / (lotte_ops + opp_ops)

    lotte_score = int(base * 10) + random.randint(0,2)
    opp_score = int((1-base)*10) + random.randint(0,2)

    if lotte_score > opp_score:
        result = "롯데 승리"
    else:
        result = "상대팀 승리"

    return lotte_score, opp_score, result
