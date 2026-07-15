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

data_laporan = get_laporan_mingguan()

df_laporan = pd.DataFrame(data_laporan)


laporan_terbaru = df_laporan.iloc[0]
hasil = laporan_terbaru["hasil_laporan"]

periode_awal = hasil["periode"]["awal"]
periode_akhir = hasil["periode"]["akhir"]
jumlah_artikel = hasil["jumlah_artikel"]
arah_ihsg = hasil["indikasi_ihsg"]["arah"]
keyakinan = hasil["indikasi_ihsg"]["tingkat_keyakinan"]
ringkasan = hasil["ringkasan_pasar"]

st.title("Market News Monitor")
st.caption(f"Periode analisis: {periode_awal} sampai {periode_akhir}")
st.caption("Ringkasan pemberitaan saham mingguan")


kolom1, kolom2, kolom3 , = st.columns(3)

kolom1.metric("Artikel dianalisis", jumlah_artikel)
kolom2.metric("Arah IHSG", arah_ihsg)
kolom3.metric("Tingkat keyakinan", keyakinan)

st.subheader("Ringkasan Pasar")
st.write(ringkasan)

st.dataframe(df_laporan)