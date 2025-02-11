from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from fastapi import FastAPI

app = FastAPI()

# Function to run every two weeks
def run_every_two_weeks():
    print("Executing scheduled task...")
    # Add your logic here (e.g., updating database, sending emails, etc.)

# Create and configure scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_every_two_weeks, IntervalTrigger(weeks=2))
scheduler.start()

print("--------------------------------Scheduler System Started--------------------------------")

# Ensure the scheduler shuts down properly when the application stops
# import atexit
# atexit.register(lambda: scheduler.shutdown())
