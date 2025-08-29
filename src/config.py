import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HF_API_TOKEN = os.getenv('HF_API_TOKEN')
    HF_MODEL_ID = os.getenv('HF_MODEL_ID')
    REQUEST_TIMEOUT_SECONDS = os.getenv('REQUEST_TIMEOUT_SECONDS', 25)
    TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY')