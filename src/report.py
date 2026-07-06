import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import ast
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from datetime import datetime
import os
from sentiment import sentiment_analysis_lexicon_indonesia
from db.database import get_article_proses, upload_plot, update_sentimen

data = get_article_proses()
clean_df = pd.DataFrame(data)
clean_df['text_akhir'] = clean_df['text_akhir']
results = clean_df['text_akhir'].apply(sentiment_analysis_lexicon_indonesia)
results = list(zip(*results))
clean_df['polarity_score'] = results[0]
clean_df['polarity'] = results[1]

tanggal = datetime.now().strftime('%Y-%m-%d')

plt.figure(figsize=(8, 5))
ax = sns.countplot(x='polarity', data=clean_df)
for container in ax.containers:
    ax.bar_label(container)
plt.title('Distribusi Sentimen')
plt.savefig('/tmp/sentiment_dist.png')
plt.close()
upload_plot('/tmp/sentiment_dist.png', f'sentiment_dist_{tanggal}.png')

semua_kata = ' '.join(clean_df['text_akhir'].dropna())
wc = WordCloud(width=800, height=400, background_color='white').generate(semua_kata)
plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title('Kata Paling Sering Muncul')
plt.savefig('/tmp/wordcloud.png')
plt.close()
upload_plot('/tmp/wordcloud.png', f'wordcloud_{tanggal}.png')

for _, row in clean_df.iterrows():
    update_sentimen(row['url'], row['polarity'], row['polarity_score'])

if 'tanggal_scrape' in clean_df.columns:
    clean_df['tanggal_scrape'] = pd.to_datetime(clean_df['tanggal_scrape']).dt.date
    tren = clean_df.groupby(['tanggal_scrape', 'polarity']).size().unstack(fill_value=0)
    tren.plot(kind='bar', figsize=(10, 5))
    plt.title('Tren Sentimen per Hari')
    plt.savefig('/tmp/tren_sentimen.png')
    plt.close()
    upload_plot('/tmp/tren_sentimen.png', f'tren_{tanggal}.png')

print("berhasil diupload.")