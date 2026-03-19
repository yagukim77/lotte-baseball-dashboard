
import os
from playwright.sync_api import sync_playwright

OUTDIR = "debug_artifacts"

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        urls = {
            "hitter": "https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter",
            "pitcher": "https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher",
            "schedule": "https://m.sports.naver.com/kbaseball/schedule/index"
        }

        for name, url in urls.items():
            page.goto(url)
            page.wait_for_timeout(5000)
            txt = page.locator("body").inner_text()
            with open(f"{OUTDIR}/{name}.txt","w",encoding="utf-8") as f:
                f.write(txt)

        browser.close()

if __name__ == "__main__":
    main()
