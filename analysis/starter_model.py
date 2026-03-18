import pandas as pd

DEFAULT_ERA = 4.50


def _safe_float(x, default=4.50):
    try:
        return float(x)
    except Exception:
        return default


def get_pitcher_era(name: str) -> float:
    if not name or str(name).strip() == "":
        return DEFAULT_ERA

    try:
        df = pd.read_csv("data/pitcher_stats.csv").copy()
    except Exception:
        return DEFAULT_ERA

    if df.empty or "player" not in df.columns or "era" not in df.columns:
        return DEFAULT_ERA

    target = df[df["player"].astype(str).str.strip() == str(name).strip()]
    if target.empty:
        return DEFAULT_ERA

    return _safe_float(target.iloc[0]["era"], DEFAULT_ERA)


def get_team_starter_avg_era(team_name: str) -> float:
    try:
        df = pd.read_csv("data/pitcher_stats.csv").copy()
    except Exception:
        return DEFAULT_ERA

    if df.empty or not {"team", "era"}.issubset(df.columns):
        return DEFAULT_ERA

    team_df = df[df["team"].astype(str).str.strip() == str(team_name).strip()].copy()
    if team_df.empty:
        return DEFAULT_ERA

    team_df["era"] = pd.to_numeric(team_df["era"], errors="coerce").fillna(DEFAULT_ERA)

    # 너무 경기수 적은 투수나 마무리/계투 노이즈가 있어도 평균치 fallback 목적이니 단순 평균 사용
    return round(team_df["era"].mean(), 2)


def get_starter_effective_era(team_name: str, starter_name: str = "") -> float:
    if starter_name and str(starter_name).strip() != "":
        return get_pitcher_era(starter_name)
    return get_team_starter_avg_era(team_name)


def era_to_pitching_score(era: float) -> float:
    # ERA 낮을수록 점수 높게
    score = max(1.0, 6.8 - float(era))
    return round(score, 2)


def adjust_attack_by_pitcher(team_attack: float, opp_team: str, opp_starter_name: str = "") -> float:
    opp_era = get_starter_effective_era(opp_team, opp_starter_name)
    opp_pitch_score = era_to_pitching_score(opp_era)

    adjusted = float(team_attack) - (opp_pitch_score - 2.0) * 0.22
    return round(max(2.0, adjusted), 2)
