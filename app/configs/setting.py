import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "heyhey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:@pritesh9988gupta@db.rhkeauffgdjefhptnwjn.supabase.co:5432/postgres")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "123")
    JWT_TOKEN_LOCATION = ["cookies"]  # Store JWT in cookies
    JWT_COOKIE_CSRF_PROTECT = False   # Disable CSRF for simplicity (enable in production)
