def clamp(x, low=0.001, high=0.999):
    return max(low, min(high, x))


def inning_weight(status_text: str) -> float:
    t = str(status_text)
    if "종료" in t:
        return 1.0
    if "9회" in t:
        return 1.0
    if "8회" in t:
        return 0.88
    if "7회" in t:
        return 0.76
    if "6회" in t:
        return 0.64
    if "5회" in t:
        return 0.52
    if "4회" in t:
        return 0.40
    if "3회" in t:
        return 0.28
    if "2회" in t:
        return 0.18
    if "1회" in t:
        return 0.10
    return 0.05


def tune_live_win_prob(base_prob: float, lotte_score: int, opp_score: int, status: str, is_home: bool):
    diff = int(lotte_score) - int(opp_score)
    w = inning_weight(status)

    if "종료" in str(status):
        if diff > 0:
            return 0.999
        if diff < 0:
            return 0.001
        return 0.5

    # 점수차를 강하게
    score_bonus = diff * (0.045 + 0.055 * w)

    # 후반일수록 훨씬 크게 반영
    late_bonus = diff * (0.02 * w)

    # 홈팀 미세 보정
    home_bonus = 0.012 if is_home else -0.012

    tuned = base_prob + score_bonus + late_bonus + home_bonus
    return clamp(tuned)
