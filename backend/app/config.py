# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env automatically

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ENV = os.getenv("ENV", "development")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-pro")