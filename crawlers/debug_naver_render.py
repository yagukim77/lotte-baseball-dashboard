import os
from playwright.sync_api import sync_playwright

OUTDIR = "debug_artifacts"
URLS = {
    "hitter": "https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter",
    "pitcher": "https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher",
    "schedule": "https://m.sports.naver.com/kbaseball/schedule/index",
}

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1440, "height": 2200})
        for name, url in URLS.items():
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            with open(os.path.join(OUTDIR, f"{name}.txt"), "w", encoding="utf-8") as f:
                f.write(page.locator("body").inner_text())
        browser.close()

if __name__ == "__main__":
    main()
