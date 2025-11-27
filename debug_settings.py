import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

print(f"BASE_DIR: {BASE_DIR}")
print(f"SECRET_KEY: {env('SECRET_KEY', default='Not Found')}")
print(f"DEBUG: {env.bool('DEBUG', default=False)}")
print(f"DATABASE_URL: {env.db('DATABASE_URL', default='Not Found')}")
