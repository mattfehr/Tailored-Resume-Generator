# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env automatically

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ENV = os.getenv("ENV", "development")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-pro")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_JWT_SECRET=os.getenv("SUPABASE_JWT_SECRET")
