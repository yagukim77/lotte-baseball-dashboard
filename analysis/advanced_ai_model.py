from analysis.team_stats import team_attack_power, recent_form
from analysis.starter_model import adjust_attack_by_starter
from analysis.team_elo import get_team_elo

def safe_recent_form_score():
    try:
        wins, loses, avg_score, avg_allowed = recent_form()
        games = wins + loses
        if games == 0:
            return 0.5
        return round(wins / games, 3)
    except Exception:
        return 0.5

def build_pregame_prediction(home_team: str, away_team: str, away_starter: str = "", home_starter: str = ""):
    away_attack = team_attack_power(away_team)
    home_attack = team_attack_power(home_team)

    away_attack_adj = adjust_attack_by_starter(away_attack, home_starter)
    home_attack_adj = adjust_attack_by_starter(home_attack, away_starter)

    away_elo = get_team_elo(away_team)
    home_elo = get_team_elo(home_team)

    form_score = safe_recent_form_score()

    home_adv = 0.03

    raw_home = (
        0.25 * (home_attack_adj / max(home_attack_adj + away_attack_adj, 1))
        + 0.20 * (home_elo / max(home_elo + away_elo, 1))
        + 0.15 * form_score
        + home_adv
    )

    raw_away = (
        0.25 * (away_attack_adj / max(home_attack_adj + away_attack_adj, 1))
        + 0.20 * (away_elo / max(home_elo + away_elo, 1))
        + 0.15 * (1 - form_score)
    )

    total = raw_home + raw_away
    home_prob = round(raw_home / total, 3)
    away_prob = round(raw_away / total, 3)

    expected_home_score = round(home_attack_adj, 1)
    expected_away_score = round(away_attack_adj, 1)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_prob": home_prob,
        "away_prob": away_prob,
        "home_score": expected_home_score,
        "away_score": expected_away_score,
        "home_elo": home_elo,
        "away_elo": away_elo,
        "home_attack": home_attack_adj,
        "away_attack": away_attack_adj,
    }
