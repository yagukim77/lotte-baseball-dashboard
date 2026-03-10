def summarize(text):

    sentences = text.split(".")

    if len(sentences) > 2:

        return sentences[0] + "." + sentences[1]

    return text
