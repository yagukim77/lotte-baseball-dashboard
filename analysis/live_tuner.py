def clamp(x, low=0.01, high=0.99):
    return max(low, min(high, x))

def get_inning_weight(status_text: str) -> float:
    t = str(status_text)
    if "종료" in t:
        return 1.0
    if "9회" in t:
        return 0.95
    if "8회" in t:
        return 0.85
    if "7회" in t:
        return 0.75
    if "6회" in t:
        return 0.65
    if "5회" in t:
        return 0.55
    if "4회" in t:
        return 0.45
    if "3회" in t:
        return 0.35
    if "2회" in t:
        return 0.25
    if "1회" in t:
        return 0.15
    return 0.05

def tune_live_win_prob(base_prob: float, lotte_score: int, opp_score: int, status: str, is_home: bool):
    diff = int(lotte_score) - int(opp_score)
    inning_weight = get_inning_weight(status)

    if "종료" in str(status):
        if diff > 0:
            return 0.999
        if diff < 0:
            return 0.001
        return 0.5

    score_bonus = diff * (0.03 + inning_weight * 0.03)
    home_bonus = 0.01 if is_home else -0.01

    tuned = base_prob + score_bonus + home_bonus
    return clamp(tuned)
