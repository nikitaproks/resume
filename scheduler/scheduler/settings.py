import os

from dotenv import load_dotenv

load_dotenv()
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
