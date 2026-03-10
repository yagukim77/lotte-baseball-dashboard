from collections import Counter
import re

def extract_keywords(titles):

    words = []

    for t in titles:

        w = re.findall(r"[가-힣]{2,}", t)

        words.extend(w)

    counter = Counter(words)

    common = counter.most_common(10)

    return common

import random

def predict_win():

    return round(random.uniform(0.45,0.65),2)
