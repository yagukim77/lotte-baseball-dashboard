def short_game_comment(win_prob: float, status: str, score_diff: int):
    if "종료" in str(status):
        if score_diff > 0:
            return "경기 종료, 롯데 승리."
        elif score_diff < 0:
            return "경기 종료, 롯데 패배."
        return "경기 종료, 무승부 흐름."

    if win_prob >= 0.7:
        return "현재 흐름은 롯데 우세입니다."
    if win_prob <= 0.3:
        return "현재 흐름은 상대팀 우세입니다."
    return "아직 승부가 팽팽합니다."

def build_today_brief(home_team, away_team, home_prob, away_prob, home_starter, away_starter):
    return {
        "matchup": f"{away_team} vs {home_team}",
        "home_prob_text": f"{home_team} {home_prob*100:.1f}%",
        "away_prob_text": f"{away_team} {away_prob*100:.1f}%",
        "home_starter": home_starter if home_starter else "미정",
        "away_starter": away_starter if away_starter else "미정",
    }
