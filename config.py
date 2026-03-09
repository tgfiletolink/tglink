import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    # Final check
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        print("Error: Required environment variables are missing.")
        print("Please check your .env file or environment.")
