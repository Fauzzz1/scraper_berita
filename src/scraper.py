import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import pandas as pd
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException
from googlenewsdecoder import gnewsdecoder
from db.database import insert_article_raw

def ambilurl(url):
  headers = {"User-Agent": "Mozilla/5.0"}
  res = requests.get(url, headers=headers)
  soup = BeautifulSoup(res.text, "xml")

  title = soup.find("title")
  print(title.get_text(strip=True))

  if "Halaman Tidak Ditemukan" in title.get_text():
    print("URL salah / artikel tidak ditemukan")
  else:
    print("URL valid")
  return soup

def ceklink(soup):
  links = soup.find_all('link')
  for linkt in links[:50]:
    print(linkt)
  return linkt
  print("Jumlah link:", len(links))

def main(test):
    interval_time = 1
    hasil = []
    source_url = test.find_all('link')
    for link in source_url[:50]:
        try:
          decoded_url = gnewsdecoder(link.text, interval=interval_time)

          if decoded_url.get("status"):
            print("Decoded URL:", decoded_url["decoded_url"])
            hasil.append(decoded_url["decoded_url"])
          else:
            print("Error:", decoded_url["message"])

        except Exception as e:
          print(f"Error occurred: {e}")
    return hasil

def ambil_isi_artikel(test):
  m = []
  for link in test:
    try:
      article = Article(link)
      article.download()
      article.parse()

      m.append({
      "url": link,
      "judul": article.title,
      "isi_artikel": article.text,
      "tanggal": article.publish_date})
    except ArticleException as e:
      print(f"Error processing URL {link}: {e}")
    except Exception as e:
      print(f"An unexpected error occurred for URL {link}: {e}")
  return m

soup = ambilurl('https://news.google.com/rss/search?q=saham&hl=id&gl=ID&ceid=ID:id')
final_url = main(soup)
hasil_artikel = ambil_isi_artikel(final_url)
df = pd.DataFrame(hasil_artikel)
df = df.dropna(subset=['isi_artikel', 'judul'])
df = df[df['isi_artikel'] != '']
for _, row in df.iterrows():
    insert_article_raw({
        "url": row["url"],
        "judul": row["judul"],
        "isi_artikel": row["isi_artikel"],
        "tanggal": str(row["tanggal"]) if pd.notna(row["tanggal"]) else None
    })

print(f"Berhasil insert {len(df)} artikel ke database.")