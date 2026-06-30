import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/mf_tracker.db")
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 30))
REQUEST_RETRY_COUNT = int(os.getenv("REQUEST_RETRY_COUNT", 3))
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")
