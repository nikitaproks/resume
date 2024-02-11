import logging
import time
from datetime import datetime

from schedule import every, run_pending

from scheduler.settings import BACKEND_API_KEY
from scheduler.utils import BackendAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def is_working_hours() -> bool:
    now = datetime.utcnow()
    if now.hour <= 9 or now.hour >= 22:
        return False
    if now.weekday() in [5, 6]:
        return False
    return True


def job():
    if not is_working_hours():
        logging.info("It's not working hours")
        return

    backend_api = BackendAPI(BACKEND_API_KEY)
    response = backend_api.trigger_analysis()
    if response.status != 200:
        logging.error("Failed to trigger analysis")
        return


def main():
    every(3).seconds.do(job)
    while True:
        run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
