import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
from db.database import get_article_proses, get_laporan_mingguan
st.set_page_config(
    page_title="Market News Monitor",
    layout="wide"
)

#import db
data_laporan = get_laporan_mingguan()
data_proses = get_article_proses()

df_laporan = pd.DataFrame(data_laporan)
df_proses = pd.DataFrame(data_proses)

laporan_terbaru = df_laporan.iloc[0]
laporan_proses = df_proses.iloc[0]
#load kolom
hasil = laporan_terbaru["hasil_laporan"]
periode_awal = hasil["periode"]["awal"]
periode_akhir = hasil["periode"]["akhir"]
jumlah_artikel = hasil["jumlah_artikel"]
arah_ihsg = hasil["indikasi_ihsg"]["arah"]
keyakinan = hasil["indikasi_ihsg"]["tingkat_keyakinan"]
ringkasan = hasil["ringkasan_pasar"]

#header
st.title("Market News Monitor")
st.caption(f"Periode analisis: {periode_awal} sampai {periode_akhir}")
st.caption("Ringkasan pemberitaan saham mingguan")

#create kolom
kolom1, kolom2, kolom3 , = st.columns(3)

kolom1.metric("Artikel dianalisis", jumlah_artikel)
kolom2.metric("Arah IHSG", arah_ihsg)
kolom3.metric("Tingkat keyakinan", keyakinan)

st.subheader("Ringkasan Pasar")
st.write(ringkasan)

# st.dataframe(df_laporan)
#manipulasi date str => date
#periodeawal-akhir
periode_awal = pd.to_datetime(
    laporan_terbaru["periode_awal"]
).date()

periode_akhir = pd.to_datetime(
    laporan_terbaru["periode_akhir"]
).date()

data = df_proses.copy()
data['tanggal'] = pd.to_datetime(
    data["tanggal_proses"]
).dt.date


info_mingguan = df_laporan.info()
info_proses = df_proses.info()
print(type(periode_awal))
print(type(periode_akhir))


#filter
data_mingguan = data[
    (data['tanggal'] >= periode_awal) &
    (data['tanggal'] <= periode_akhir)
]

#menampilkan anomali saham
st.subheader("Daftar Anomali Saham Mingguan")
for anomali in hasil["anomali_saham"]:
    ticker = anomali["ticker"]
    alasan = anomali["alasan"]
    st.write(ticker)
    st.write(alasan)
    
#sentimen
sentimen = data_mingguan['sentimen']
visualisasi = sentimen.value_counts()

#visualisasi
st.bar_chart(visualisasi, width=400, height=400)