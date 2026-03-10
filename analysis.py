import re
from collections import Counter
import random

stopwords = [
"롯데","자이언츠","프로야구","KBO",
"경기","선수","감독","시즌","구단"
]

def extract_keywords(texts):

    words = []

    for t in texts:

        tokens = re.findall(r"[가-힣]{2,}", str(t))

        for w in tokens:

            if w not in stopwords:

                words.append(w)

    counter = Counter(words)

    return counter.most_common(20)


def predict_win():

    return round(random.uniform(0.45,0.65),2)
