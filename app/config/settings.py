import os
from dotenv import load_dotenv
from pathlib import Path


_ = load_dotenv()

class Settings:
    
    APP_NAME = os.getenv("APP_NAME","Chat with Files")
    VERSION = os.getenv("VERSION","1.0.0")
    API_KEY = os.getenv("API_KEY")

    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)


    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-2.0-flash"
    EMBEDDING_MODEL_NAME = "gemini-embedding-001"
    TEMPERATURE = 0.5
    MAX_TOKENS = 1024
    
    DATABASE_DIR  = os.path.join(BASE_DIR,"database")
    os.makedirs(DATABASE_DIR, exist_ok=True)

    HISTORY_DIR = os.path.join(DATABASE_DIR, "history")
    os.makedirs(HISTORY_DIR, exist_ok=True)
    MAX_SESSIONS = 10

    LOG_LEVEL = os.getenv("LOG_LEVEL","INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "app.log"
    
settings = Settings()