from analysis.team_stats import team_attack_power
from analysis.team_elo import get_team_elo
from analysis.recent_form_strength import get_recent_form_strength
from analysis.starter_model import adjust_attack_by_pitcher, get_starter_effective_era
from analysis.park_factor import get_park_factor
from analysis.weekday_factor import get_weekday_factor
from analysis.home_away_split import get_home_away_split_factor


def _normalize_pair(a, b):
    s = a + b
    if s == 0:
        return 0.5, 0.5
    return a / s, b / s


def build_tuned_prediction(home_team, away_team, game_date="", stadium="", home_starter="", away_starter="", lineup_boost_home=None, lineup_boost_away=None):
    home_attack = team_attack_power(home_team)
    away_attack = team_attack_power(away_team)

    # 홈/원정 분리
    home_split = get_home_away_split_factor(home_team, is_home=True)
    away_split = get_home_away_split_factor(away_team, is_home=False)

    home_attack *= home_split
    away_attack *= away_split

    # 선발 반영
    home_attack = adjust_attack_by_pitcher(home_attack, away_team, away_starter)
    away_attack = adjust_attack_by_pitcher(away_attack, home_team, home_starter)

    # 라인업 수동 입력 반영
    if lineup_boost_home is not None:
        home_attack = (home_attack * 0.7) + (lineup_boost_home * 0.3)
    if lineup_boost_away is not None:
        away_attack = (away_attack * 0.7) + (lineup_boost_away * 0.3)

    home_elo = get_team_elo(home_team)
    away_elo = get_team_elo(away_team)

    home_form = get_recent_form_strength(home_team)
    away_form = get_recent_form_strength(away_team)

    park_factor = get_park_factor(stadium)
    weekday_factor = get_weekday_factor(game_date)

    home_attack *= park_factor * weekday_factor
    away_attack *= park_factor * weekday_factor

    attack_h, attack_a = _normalize_pair(home_attack, away_attack)
    elo_h, elo_a = _normalize_pair(home_elo, away_elo)
    form_h, form_a = _normalize_pair(home_form["strength_score"], away_form["strength_score"])

    # 가중치
    home_prob = (
        0.30 * attack_h +
        0.25 * elo_h +
        0.20 * form_h +
        0.10 * 0.52 +    # 홈 어드밴티지
        0.15 * (1 if home_attack >= away_attack else 0.45)
    )

    away_prob = (
        0.30 * attack_a +
        0.25 * elo_a +
        0.20 * form_a +
        0.10 * 0.48 +
        0.15 * (1 if away_attack > home_attack else 0.45)
    )

    total = home_prob + away_prob
    home_prob = round(home_prob / total, 3)
    away_prob = round(away_prob / total, 3)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_prob": home_prob,
        "away_prob": away_prob,
        "home_score": round(home_attack, 1),
        "away_score": round(away_attack, 1),
        "home_elo": round(home_elo, 1),
        "away_elo": round(away_elo, 1),
        "home_form": home_form,
        "away_form": away_form,
        "home_starter_era": get_starter_effective_era(home_team, home_starter),
        "away_starter_era": get_starter_effective_era(away_team, away_starter),
        "park_factor": park_factor,
        "weekday_factor": weekday_factor,
        "home_attack": round(home_attack, 2),
        "away_attack": round(away_attack, 2),
    }
