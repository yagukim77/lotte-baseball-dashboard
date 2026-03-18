import requests

def get_live_score():

    try:
        url = "https://www.koreabaseball.com"

        r = requests.get(url, timeout=5)

        if "롯데" in r.text:
            return "⚾ 롯데 경기 진행중"

        return "오늘 롯데 경기 없음"

    except:
        return "경기 정보 불러오기 실패"