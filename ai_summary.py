def summarize(text):

    if not isinstance(text,str):
        return ""

    sentences = text.split(".")

    if len(sentences) > 2:

        return sentences[0] + "." + sentences[1]

    return text[:150]
