import random

def simulate_game():

    lotte = random.randint(2,9)
    opponent = random.randint(1,8)

    if lotte > opponent:
        result = "롯데 승리"
    else:
        result = "상대팀 승리"

    return lotte, opponent, result
