import sys
import os
import schedule
import time
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def jalankan_pipeline():
    print("Menjalankan pipeline...")
    subprocess.run(['python', 'scraper.py'])
    subprocess.run(['python', 'cleaning.py'])
    subprocess.run(['python', 'report.py'])
    print("Pipeline selesai.")

schedule.every().day.at("08:00").do(jalankan_pipeline)

print("Scheduler berjalan...")
while True:
    schedule.run_pending()
    time.sleep(1)