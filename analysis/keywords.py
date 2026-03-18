from collections import Counter
import re

def extract_keywords(titles):

    words = []

    for t in titles:

        w = re.findall(r"[가-힣]{2,}", str(t))

        words.extend(w)

    counter = Counter(words)

    common = counter.most_common(10)

    return common