import schedule
import time
from multi_runner import run_multiple

def job():
    print("Running scheduled stock prediction...")
    run_multiple()

schedule.every().day.at("09:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)