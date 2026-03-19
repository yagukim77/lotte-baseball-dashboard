import os
import traceback
from datetime import datetime

OUTDIR = "debug_artifacts"

def write_text(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    # 무조건 생성되는 파일
    write_text(
        os.path.join(OUTDIR, "00_start.txt"),
        "\n".join([
            f"started_at={datetime.now().isoformat()}",
            f"cwd={os.getcwd()}",
            f"outdir_abs={os.path.abspath(OUTDIR)}",
            f"files_in_cwd={os.listdir('.')}",
        ])
    )

    try:
        from playwright.sync_api import sync_playwright

        URLS = {
            "naver_main": "https://m.sports.naver.com/index",
            "naver_kbo_schedule": "https://m.sports.naver.com/kbaseball/schedule/index",
            "naver_kbo_record_hitter": "https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter",
            "naver_kbo_record_pitcher": "https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher",
            "kbo_schedule": "https://www.koreabaseball.com/Schedule/Schedule.aspx",
            "kbo_gamecenter": "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx",
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page(viewport={"width": 1440, "height": 2200})

            for name, url in URLS.items():
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(5000)

                    html = page.content()
                    body_text = page.locator("body").inner_text()

                    write_text(os.path.join(OUTDIR, f"{name}.html"), html)
                    write_text(os.path.join(OUTDIR, f"{name}.txt"), body_text)
                    page.screenshot(path=os.path.join(OUTDIR, f"{name}.png"), full_page=True)

                    info = [
                        f"name={name}",
                        f"url={url}",
                        f"body_text_len={len(body_text)}",
                        f"table_count={page.locator('table').count()}",
                        f"tr_count={page.locator('table tbody tr').count()}",
                        f"div_count={page.locator('div').count()}",
                        f"span_count={page.locator('span').count()}",
                        f"a_count={page.locator('a').count()}",
                    ]
                    write_text(os.path.join(OUTDIR, f"{name}_meta.txt"), "\n".join(info))

                except Exception as e:
                    write_text(
                        os.path.join(OUTDIR, f"{name}_error.txt"),
                        f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
                    )

            browser.close()

    except Exception as e:
        write_text(
            os.path.join(OUTDIR, "99_fatal_error.txt"),
            f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        )

    # 마지막에 현재 생성 파일 목록 저장
    write_text(
        os.path.join(OUTDIR, "98_file_list.txt"),
        "\n".join(sorted(os.listdir(OUTDIR)))
    )

if __name__ == "__main__":
    main()
