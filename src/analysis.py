import sys
import json
import os
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from google import genai
from db.database import insert_article_proses ,get_article_proses
from datetime import datetime, timedelta

load_dotenv()

data = get_article_proses()
df = pd.DataFrame(data)
hari_ini = datetime.now()

periode_awal = hari_ini - timedelta(days=hari_ini.weekday())
periode_akhir = periode_awal + timedelta(days=5)

_gemini_client = None
def get_gemini_client():
    global _gemini_client

    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _gemini_client = genai.Client(api_key=api_key)

    return _gemini_client

def mingguan():
    data_mingguan = []
    for daily in data:
        if periode_awal <= daily["tanggal_proses"] <= periode_akhir:
            data_mingguan.append(daily)
    return data_mingguan
