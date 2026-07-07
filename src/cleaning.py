import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import os
import string
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from db.database import insert_article_proses
from db.database import get_articles_raw
nltk.download('punkt_tab')
nltk.download('stopwords')


data = get_articles_raw()
df = pd.DataFrame(data)
print(df.columns.tolist())
df['tanggal_scrape'] = pd.to_datetime(df['tanggal_scrape'], format='mixed', utc=True)
clean_df = df.dropna(subset=['isi_artikel'])

def cleaningText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#[A-Za-z0-9]+', '', text)
    text = re.sub(r'RT[\s]', '', text)
    text = re.sub(r"http\S+", '', text)
    text = re.sub(r'[0-9]+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.replace('\n', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip(' ')
    return text

def casefoldingText(text):
    text = text.lower()
    return text

def tokenizingText(text):
    text = word_tokenize(text)
    return text
def filteringText(text):
    listStopwords = set(stopwords.words('indonesian'))
    listStopwords1 = set(stopwords.words('english'))
    listStopwords.update(listStopwords1)

    custom_stopwords = {
        'iya', 'yaa', 'ya', 'yah',
        'loh', 'kah', 'woi', 'woii', 'woy',
        'nih', 'nihh', 'dong', 'deh', 'kok',
        'lah', 'pun', 'eh', 'oh',
        'oke', 'ok',
        'hehe', 'haha', 'hahaha',
        'wkwk', 'wk'
    }

    important_words = {
        'tidak', 'bukan', 'belum', 'jangan',
        'naik', 'turun', 'menguat', 'melemah',
        'beli', 'jual', 'borong', 'lepas',
        'laba', 'rugi', 'untung',
        'cuan', 'loss',
        'saham', 'emiten', 'ihsg', 'bei',
        'investor', 'asing',
        'dividen', 'ipo',
        'anjlok', 'meroket',
        'positif', 'negatif'
    }

    listStopwords.update(custom_stopwords)
    listStopwords.difference_update(important_words)

    filtered = [txt for txt in text if txt not in listStopwords]
    return filtered

def stemmingText(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)

def toSentence(list_words):
    return ' '.join(word for word in list_words)

slangwords = {
    "dr": "dari",
    "utk": "untuk",
    "yg": "yang",
    "jd": "jadi",
    "krn": "karena",
    "karna": "karena",
    "tp": "tetapi",
    "tpi": "tetapi",
    "dgn": "dengan",
    "dll": "dan lain lain",

    "ga": "tidak",
    "gak": "tidak",
    "gk": "tidak",
    "ngga": "tidak",
    "nggak": "tidak",
    "engga": "tidak",
    "enggak": "tidak",

    "emiten2": "emiten",
    "saham2": "saham",
    "investor2": "investor"
}

def fix_slangwords(text):
    words = text.split()
    fixed_words = [slangwords[word.lower()] if word.lower() in slangwords else word for word in words]
    return ' '.join(fixed_words)

clean_df['text_clean'] = clean_df['isi_artikel'].apply(cleaningText)
clean_df['text_casefoldingText'] = clean_df['text_clean'].apply(casefoldingText)
clean_df['text_slangwords'] = clean_df['text_casefoldingText'].apply(fix_slangwords)
clean_df['text_tokenizingText'] = clean_df['text_slangwords'].apply(tokenizingText)
clean_df['text_stopword'] = clean_df['text_tokenizingText'].apply(filteringText)
clean_df['text_akhir'] = clean_df['text_stopword'].apply(toSentence)

for _, row in clean_df.iterrows():
    insert_article_proses({
        "url": row["url"],
        "text_clean": row["text_clean"],
        "text_akhir": row["text_akhir"],
        "sentimen": None,
        "polarity_score": None
    })

print(f"Berhasil insert {len(clean_df)} artikel ke articles_processed.")