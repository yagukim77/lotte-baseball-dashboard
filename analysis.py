from collections import Counter
import re
import random


# 키워드 분석
def extract_keywords(titles):

    words = []

    # 불필요 단어 제거
    stopwords = [
        "롯데","자이언츠","프로야구","KBO",
        "경기","오늘","선수","감독","시즌"
    ]

    for t in titles:

        # 한글 단어 추출
        w = re.findall(r"[가-힣]{2,}", str(t))

        for word in w:

            if word not in stopwords:

                words.append(word)

    counter = Counter(words)

    common = counter.most_common(10)

    return common


# 롯데 승리 확률 예측 (간단 버전)
def predict_win():

    win_rate = random.uniform(0.45, 0.65)

    return round(win_rate, 2)
