import os

from dotenv import load_dotenv

load_dotenv()
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
TRIGGER_INTERVAL_SECONDS = int(os.getenv("TRIGGER_INTERVAL_SECONDS", 3600))
