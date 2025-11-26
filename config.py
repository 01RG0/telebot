"""
Configuration file for the Telegram bot application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8334074221:AAE8pGbyawYLnZmDlQd4fRXoW0p0hvO7koY")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "telegram_bot")
USERS_COLLECTION = "users"

# Application Settings
SEND_DELAY = float(os.getenv("SEND_DELAY", "0.5"))  # seconds between sends
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "اهلا بيك في نظام المتابعة لمستر شادي الشرقاوي شكرا على ثقتك بنتمنى نكون عند حسن ظنك")

# Logging Configuration
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# GUI Configuration
WINDOW_TITLE = "Telegram Admin - Mr Shady"
WINDOW_SIZE = "980x660"
