import sys
import json
import os
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from google import genai
from db.database import insert_article_proses ,get_article_proses , get_laporan_mingguan
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

def mingguan(data, periode_awal, periode_akhir):
    data_mingguan = []
    format_tanggal = "%Y-%m-%dT%H:%M:%S.%f%z"

    
    for artikel in data:
        tanggal_proses = datetime.fromisoformat(artikel["tanggal_proses"])
        tanggal_naive = tanggal_proses.replace(tzinfo=None)
        if periode_awal <= tanggal_naive <= periode_akhir:
            data_mingguan.append(artikel)

    return data_mingguan

data_mingguan = mingguan(data, periode_awal, periode_akhir)

prompt = f"""
Anda adalah analis berita saham Indonesia.

buar rangkuman mengenai anomali saham yang kemungkinan naik 
Isi:
{data_mingguan}

Balas hanya dalam JSON dengan struktur:
{{
  "ringkasan": ""
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

print(data_laporan)