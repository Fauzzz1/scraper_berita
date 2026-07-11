import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def insert_article_raw(data):
    try:
        supabase.table("articles_raw").upsert(data, on_conflict="url").execute()
    except Exception as e:
        print(f"Error : {e}")

def get_articles_raw():
    response = supabase.table("articles_raw").select("*").execute()
    return response.data

def insert_article_proses(data):
    try:
        supabase.table("article_proses").upsert(data, on_conflict="url").execute()
    except Exception as e:
        print(f"Error : {e}")

def get_article_proses():
    response = supabase.table("article_proses").select("*").execute()
    return response.data

def insert_laporan_mingguan(data):
    return (
        supabase
        .table("laporan_mingguan")
        .upsert(
            data,
            on_conflict="periode_awal,periode_akhir"
        )
        .execute()
    )
        
def get_laporan_mingguan():
    response = supabase.table("laporan_mingguan").select("*").execute()
    return response.data

def upload_plot(file_path, file_name):
    with open(file_path, 'rb') as f:
        supabase.storage.from_('plots').upload(
            file_name,
            f,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
    url = supabase.storage.from_('plots').get_public_url(file_name)
    return url
    
def update_sentimen(url, sentimen, polarity_score):
    try:
        supabase.table("article_proses").update({
            "sentimen": sentimen,
            "polarity_score": polarity_score
        }).eq("url", url).execute()
    except Exception as e:
        print(f"Error update sentimen: {e}")