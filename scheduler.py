from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline import run_pipeline
from datetime import datetime

scheduler = BlockingScheduler()

@scheduler.scheduled_job("cron", hour=7, minute=0)
def scheduled_job():
    print(f"scheduled run at {datetime.now()}")
    run_pipeline()
