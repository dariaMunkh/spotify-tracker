import schedule
import time
from pipeline import run_pipeline

# Run immediately on start
run_pipeline()

# Then run every 24 hours
schedule.every(24).hours.do(run_pipeline)

print("Scheduler running... pipeline will update every 24 hours")
print("Keep this window open. Press CTRL+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)