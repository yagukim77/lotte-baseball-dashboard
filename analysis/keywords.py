from collections import Counter
import re

def extract_keywords(titles):

    words=[]

    for t in titles:

        w=re.findall(r"[가-힣]{2,}",t)

        words.extend(w)

    counter=Counter(words)

    return counter.most_common(10)
