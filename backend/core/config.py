import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
DIGIKEY_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID", "")
DIGIKEY_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET", "")
MOUSER_API_KEY = os.getenv("MOUSER_API_KEY", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
DOLLAR_EXCHANGE_RATE = float(os.getenv("DOLLAR_EXCHANGE_RATE", ""))