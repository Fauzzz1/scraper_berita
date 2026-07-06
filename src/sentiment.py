import csv
import requests
from io import StringIO


def load_lexicon(url):
    lexicon = {}

    response = requests.get(url)

    if response.status_code == 200:
        reader = csv.reader(StringIO(response.text))

        for word, score in reader:
            lexicon[word] = int(score)
    else:
        print(f"Gagal mengambil data dari {url}")

    return lexicon


lexicon_positive = load_lexicon(
    "https://raw.githubusercontent.com/angelmetanosaa/dataset/main/lexicon_positive.csv"
)

lexicon_negative = load_lexicon(
    "https://raw.githubusercontent.com/angelmetanosaa/dataset/main/lexicon_negative.csv"
)


def sentiment_analysis_lexicon_indonesia(text):
    if isinstance(text, str):
        text = text.split()

    score = 0

    for word in text:
        if word in lexicon_positive:
            score += lexicon_positive[word]

        if word in lexicon_negative:
            score += lexicon_negative[word]

    if score > 0:
        polarity = "positive"
    elif score < 0:
        polarity = "negative"
    else:
        polarity = "neutral"

    return score, polarity