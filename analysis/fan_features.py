def short_game_comment(win_prob: float, status: str, score_diff: int):
    if "종료" in str(status):
        if score_diff > 0:
            return "경기 종료, 롯데 승리입니다."
        if score_diff < 0:
            return "경기 종료, 롯데 패배입니다."
        return "경기 종료, 팽팽한 결과였습니다."

    if win_prob >= 0.8:
        return "현재 흐름은 롯데가 확실히 우세합니다."
    if win_prob >= 0.65:
        return "현재 흐름은 롯데 우세입니다."
    if win_prob <= 0.2:
        return "현재 흐름은 상대팀이 확실히 우세합니다."
    if win_prob <= 0.35:
        return "현재 흐름은 상대팀 우세입니다."
    return "아직 승부가 팽팽합니다."


def explain_prediction(home_prob, away_prob, home_attack, away_attack, home_elo, away_elo):
    reason = []

    if home_attack > away_attack:
        reason.append("홈팀 공격력이 더 높음")
    elif away_attack > home_attack:
        reason.append("원정팀 공격력이 더 높음")

    if home_elo > away_elo:
        reason.append("홈팀 ELO 우세")
    elif away_elo > home_elo:
        reason.append("원정팀 ELO 우세")

    if home_prob > away_prob:
        reason.append("홈 어드밴티지 반영")
    else:
        reason.append("원정 전력 우세 반영")

    return " / ".join(reason[:3])
