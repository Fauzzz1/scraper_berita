import sys
import json
import os
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from google import genai
from db.database import insert_article_proses ,insert_laporan_mingguan ,get_article_proses , get_laporan_mingguan
from datetime import datetime, timedelta

load_dotenv()

data = get_article_proses()
hari_ini = datetime.now()

periode_awal = hari_ini - timedelta(days=hari_ini.weekday())
periode_akhir = periode_awal + timedelta(days=5)

periode_awal = periode_awal.replace(tzinfo=None)
periode_akhir = periode_akhir.replace(tzinfo=None)

_gemini_client = None
def get_gemini_client():
    global _gemini_client

    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _gemini_client = genai.Client(api_key=api_key)

    return _gemini_client

def weekly(data, periode_awal, periode_akhir):
    data_mingguan = []
    format_tanggal = "%Y-%m-%dT%H:%M:%S.%f%z"

    
    for artikel in data:
        tanggal_proses = datetime.fromisoformat(artikel["tanggal_proses"])
        tanggal_naive = tanggal_proses.replace(tzinfo=None)
        if periode_awal <= tanggal_naive <= periode_akhir:
            data_mingguan.append(artikel)

    return data_mingguan

data_mingguan = weekly(data, periode_awal, periode_akhir)

konteks_artikel = json.dumps(
    data_mingguan,
    ensure_ascii=False,
    default=str
)

prompt = f"""
Anda adalah analis berita pasar saham Indonesia.

Tugas Anda adalah menganalisis kumpulan artikel pada periode:
- Awal: {periode_awal.date().isoformat()}
- Akhir: {periode_akhir.date().isoformat()}

Tujuan analisis:
1. Menemukan peristiwa atau pola pemberitaan tidak biasa yang berpotensi menjadi
   katalis bagi emiten, sektor, atau IHSG.
2. Menemukan emiten yang memperoleh sinyal positif, negatif, atau campuran
   berdasarkan berita yang tersedia.
3. Menjelaskan faktor pendorong, faktor risiko, dan bukti artikel.
4. Memberikan indikasi umum kondisi IHSG berdasarkan keseluruhan berita.

Data artikel:
{konteks_artikel}

Aturan analisis:
- Gunakan hanya informasi yang terdapat dalam data artikel.
- Jangan menambahkan fakta, ticker, angka, atau peristiwa dari luar data.
- Prioritaskan saham yang tercatat di Bursa Efek Indonesia.
- Berita global hanya boleh digunakan jika memiliki hubungan dengan IHSG,
  sektor, atau emiten Indonesia.
- Gunakan istilah "indikasi positif", "indikasi negatif", atau "campuran".
- Jangan mengubah label sentimen yang sudah terdapat pada artikel.
- Bedakan tren yang didukung beberapa artikel dengan kejadian yang hanya
  muncul dalam satu artikel.
- Jangan menyebut terjadi lonjakan dibandingkan minggu sebelumnya karena
  data pembanding periode sebelumnya tidak diberikan.
- Artikel dengan judul atau isi serupa tidak boleh dianggap sebagai bukti
  berbeda tanpa penjelasan.
- Pilih maksimal 5 anomali atau sinyal yang paling kuat.
- Tingkat keyakinan harus berupa: rendah, sedang, atau tinggi.
- Keyakinan ditentukan berdasarkan jumlah bukti, konsistensi sentimen,
  kejelasan katalis, dan keberadaan faktor risiko.
- Jika bukti tidak cukup, gunakan array kosong.
- Balas hanya dengan JSON valid tanpa Markdown atau teks tambahan.

Struktur JSON wajib:

{{
  "periode": {{
    "awal": "{periode_awal.date().isoformat()}",
    "akhir": "{periode_akhir.date().isoformat()}"
  }},
  "jumlah_artikel": {len(data_mingguan)},
  "ringkasan_pasar": "",
  "indikasi_ihsg": {{
    "arah": "menguat | melemah | netral",
    "tingkat_keyakinan": "rendah | sedang | tinggi",
    "alasan": [],
    "sektor_pendorong": [],
    "faktor_risiko": []
  }},
  "anomali_saham": [
    {{
      "ticker": "",
      "nama_emiten": "",
      "jenis_anomali": "",
      "indikasi": "positif | negatif | campuran",
      "tingkat_keyakinan": "rendah | sedang | tinggi",
      "alasan": "",
      "katalis": [],
      "faktor_risiko": [],
      "bukti_artikel": [
        {{
          "judul": "",
          "tanggal": "",
          "url": ""
        }}
      ]
    }}
  ],
  "tren_sektor": [
    {{
      "sektor": "",
      "indikasi": "positif | negatif | campuran",
      "ringkasan": "",
      "bukti_artikel": []
    }}
  ],
  "temuan_penting": [],
  "kesimpulan": ""
}}
"""
client = get_gemini_client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json"
    }
)
print(repr(response.text))
hasil_laporan = json.loads(response.text)

data_laporan = {
    "periode_awal": periode_awal.date().isoformat(),
    "periode_akhir": periode_akhir.date().isoformat(),
    "jumlah_artikel": len(data_mingguan),
    "hasil_laporan": hasil_laporan
}

insert_laporan_mingguan(data_laporan)

print(
    f"Berhasil menyimpan laporan dari {len(data_mingguan)} artikel ke database."
    f"{len(data_mingguan)} artikel ke database."
)