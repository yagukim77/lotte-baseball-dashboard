def clamp(x, low=0.01, high=0.99):
    return max(low, min(high, x))


def inning_weight(status_text: str) -> float:
    text = str(status_text)
    if "종료" in text:
        return 1.0
    for inn, weight in [("9회",0.95),("8회",0.85),("7회",0.75),("6회",0.65),("5회",0.55),("4회",0.45),("3회",0.35),("2회",0.25),("1회",0.15)]:
        if inn in text:
            return weight
    return 0.05


def score_impact(score_diff: int) -> float:
    return score_diff * 0.045


def pregame_win_prob(base_attack: float, opp_attack: float, lotte_elo: float, opp_elo: float) -> float:
    attack_term = (base_attack - opp_attack) * 0.06
    elo_term = (lotte_elo - opp_elo) / 1000.0
    p = 0.5 + attack_term + elo_term
    return clamp(p, 0.1, 0.9)


def live_win_prob(pregame_prob: float, lotte_score: int, opp_score: int, game_status: str) -> float:
    diff = int(lotte_score) - int(opp_score)
    w = inning_weight(game_status)
    if "종료" in str(game_status):
        if diff > 0:
            return 0.999
        if diff < 0:
            return 0.001
        return 0.5
    p = pregame_prob + score_impact(diff) * (0.3 + w)
    return clamp(p)
