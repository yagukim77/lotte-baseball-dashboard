from urllib.parse import quote_plus
from datetime import datetime


def build_highlight_queries(team_a: str, team_b: str) -> list[str]:
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        f"{today} {team_a} {team_b} 하이라이트",
        f"{team_a} {team_b} KBO 하이라이트",
        f"{team_a} 경기 하이라이트",
    ]


def build_youtube_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
