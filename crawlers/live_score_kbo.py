import requests

def get_live_score():

    url="https://www.koreabaseball.com"

    r=requests.get(url)

    if "롯데" in r.text:

        return "⚾ 롯데 경기 진행중"

    return "오늘 경기 없음"