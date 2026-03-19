import os
from playwright.sync_api import sync_playwright

URLS = {
    "naver_main": "https://m.sports.naver.com/index",
    "naver_kbo_schedule": "https://m.sports.naver.com/kbaseball/schedule/index",
    "naver_kbo_record_hitter": "https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter",
    "naver_kbo_record_pitcher": "https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher",
    "kbo_schedule": "https://www.koreabaseball.com/Schedule/Schedule.aspx",
    "kbo_gamecenter": "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx",
}

OUTDIR = "debug_artifacts"


def save_text(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page(viewport={"width": 1440, "height": 2200})

        for name, url in URLS.items():
            print(f"\n===== OPEN: {name} / {url} =====")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000)

                html = page.content()
                body_text = page.locator("body").inner_text()

                save_text(f"{OUTDIR}/{name}.html", html)
                save_text(f"{OUTDIR}/{name}.txt", body_text)

                page.screenshot(path=f"{OUTDIR}/{name}.png", full_page=True)

                print(f"saved: {name}.html / .txt / .png")
                print(f"body_text_len={len(body_text)}")

                selectors = {
                    "table": "table",
                    "tbody_tr": "table tbody tr",
                    "div": "div",
                    "a": "a",
                    "span": "span",
                    "button": "button",
                    "list_items": "li",
                }

                for key, selector in selectors.items():
                    try:
                        count = page.locator(selector).count()
                        print(f"{key}: {count}")
                    except Exception as e:
                        print(f"{key}: error / {e}")

                key_terms = [
                    "롯데", "LG", "두산", "삼성", "KIA", "한화", "NC", "SSG", "키움", "KT",
                    "경기전", "예정", "종료", "우천취소", "우천중단",
                    "OPS", "ERA", "타율", "평균자책"
                ]
                found = {term: (term in body_text) for term in key_terms}
                print("term_hits:", found)

            except Exception as e:
                save_text(f"{OUTDIR}/{name}_error.txt", str(e))
                print(f"ERROR: {name} / {e}")

        browser.close()


if __name__ == "__main__":
    main()
