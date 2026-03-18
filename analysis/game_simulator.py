import numpy as np

def simulate_game(teamA_attack, teamB_attack, n=1000):

    teamA_win = 0
    teamB_win = 0

    scores = []

    for i in range(n):

        scoreA = np.random.poisson(teamA_attack)
        scoreB = np.random.poisson(teamB_attack)

        scores.append((scoreA, scoreB))

        if scoreA > scoreB:
            teamA_win += 1
        elif scoreB > scoreA:
            teamB_win += 1

    return {
        "teamA_win_rate": teamA_win/n,
        "teamB_win_rate": teamB_win/n,
        "avg_scoreA": np.mean([s[0] for s in scores]),
        "avg_scoreB": np.mean([s[1] for s in scores])
    }