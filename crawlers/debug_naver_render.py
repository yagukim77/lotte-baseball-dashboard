from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse
import time

DEFAULT_URL = "https://m.sports.naver.com/kbaseball/schedule/index"


def ensure_dirs():
    Path("debug_artifacts").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)


def save_text(path: str, text: str):
    Path(path).write_text(text or "", encoding="utf-8")


def save_html(path: str, html: str):
    Path(path).write_text(html or "", encoding="utf-8")


def render_naver(url: str = DEFAULT_URL, wait_ms: int = 4000, headless: bool = True):
    """
    목적:
    - 최소한 debug_artifacts/naver_main.txt 는 무조건 생성
    - body 전체 텍스트를 score_page.txt 로도 저장
    - selector 실패로 파일이 안 생기는 문제를 피하기 위해 '항상 body 기준 백업' 저장
    """
    ensure_dirs()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1440, "height": 2200})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(wait_ms)

        # lazy render 대응
        try:
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1200)
            page.mouse.wheel(0, -1200)
            page.wait_for_timeout(1200)
        except Exception:
            pass

        html = page.content()
        body_text = ""
        try:
            body_text = page.locator("body").inner_text(timeout=10000)
        except Exception:
            body_text = ""

        # 무조건 생성되는 파일들
        save_html("debug_artifacts/naver_main.html", html)
        save_text("debug_artifacts/naver_main.txt", body_text)
        save_text("debug_artifacts/score_page.txt", body_text)

        # 후보 selector 텍스트도 추가 저장
        selector_candidates = [
            '[class*="Schedule"]',
            '[class*="schedule"]',
            '[class*="game"]',
            '[class*="Game"]',
            '[id*="content"]',
            'main',
        ]

        for i, selector in enumerate(selector_candidates, start=1):
            try:
                loc = page.locator(selector).first
                if loc.count() > 0:
                    txt = loc.inner_text(timeout=3000)
                    if txt and txt.strip():
                        save_text(f"debug_artifacts/selector_{i}.txt", txt)
            except Exception:
                continue

        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--wait-ms", type=int, default=4000)
    parser.add_argument("--show-browser", action="store_true")
    args = parser.parse_args()

    render_naver(
        url=args.url,
        wait_ms=args.wait_ms,
        headless=not args.show_browser,
    )
    print("created:")
    print("- debug_artifacts/naver_main.html")
    print("- debug_artifacts/naver_main.txt")
    print("- debug_artifacts/score_page.txt")
