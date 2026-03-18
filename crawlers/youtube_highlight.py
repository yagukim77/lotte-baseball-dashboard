import pandas as pd
from analysis.highlight_finder import build_highlight_queries, build_youtube_search_url


def build_highlight_links(team_a: str = "롯데", team_b: str = "") -> pd.DataFrame:
    queries = build_highlight_queries(team_a, team_b if team_b else "상대팀")
    rows = [{"query": q, "url": build_youtube_search_url(q)} for q in queries]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_highlight_links()
    df.to_csv("data/highlight_links.csv", index=False, encoding="utf-8-sig")
    print("saved: data/highlight_links.csv")
