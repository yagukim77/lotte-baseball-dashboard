from wordcloud import WordCloud
import matplotlib.pyplot as plt

def make_cloud(words):

    text = " ".join(words)

    wc = WordCloud(
        font_path="malgun.ttf",
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    fig, ax = plt.subplots()

    ax.imshow(wc)

    ax.axis("off")

    return fig
