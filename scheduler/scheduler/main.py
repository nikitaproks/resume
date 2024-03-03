import logging
import time

from schedule import every, run_pending

from scheduler.settings import BACKEND_API_KEY, TRIGGER_INTERVAL_SECONDS
from scheduler.utils import BackendAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# def is_working_hours() -> bool:
#     now = datetime.utcnow()
#     if now.hour <= 9 or now.hour >= 22:
#         return False
#     if now.weekday() in [5, 6]:
#         return False
#     return True


def job():
    backend_api = BackendAPI(
        "http://nginx:80/", authorization=f"Api-Key {BACKEND_API_KEY}"
    )
    response = backend_api.trigger_analysis()
    if not response:
        logging.error("Failed to trigger analysis")
        return
    if response.status != 200:
        logging.error(
            f"Analysis trigger returned {response.status} status code"
        )
        return


def main():
    every(TRIGGER_INTERVAL_SECONDS).seconds.do(job)
    while True:
        run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
