import os
import pandas as pd

def crawl_news():
    os.makedirs("data", exist_ok=True)

    try:
        # 기존 크롤링 로직 (네 코드 유지)
        data = [
            {"title": "롯데 승리"},
            {"title": "타선 폭발"}
        ]

        df = pd.DataFrame(data)

        if len(df) == 0:
            raise ValueError("news empty")

        df.to_csv("data/news.csv", index=False, encoding="utf-8-sig")
        print("saved: data/news.csv")

    except Exception as e:
        print(f"news crawler error: {e}")

        # 기존 파일 유지
        if not os.path.exists("data/news.csv"):
            pd.DataFrame(columns=["title"]).to_csv(
                "data/news.csv", index=False, encoding="utf-8-sig"
            )
            print("created empty news.csv")
