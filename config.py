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
LOG_FILE = os.getenv("LOG_FILE", os.path.join("data", "app.log"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# GUI Configuration
WINDOW_TITLE = "Telegram Admin - Mr Shady"
WINDOW_SIZE = "980x660"

# === OPTIMIZATION SETTINGS ===
# Task Queue Configuration
TASK_QUEUE_WORKERS = int(os.getenv("TASK_QUEUE_WORKERS", "2"))  # Number of worker threads for background tasks
TASK_QUEUE_ENABLED = os.getenv("TASK_QUEUE_ENABLED", "True").lower() in ("true", "1", "yes")

# Excel Processing
EXCEL_CHUNK_SIZE = int(os.getenv("EXCEL_CHUNK_SIZE", "100"))  # Process rows in chunks of N size
EXCEL_BATCH_SIZE = int(os.getenv("EXCEL_BATCH_SIZE", "50"))  # Send messages in batches

# Rate Limiting
MIN_SEND_DELAY = float(os.getenv("MIN_SEND_DELAY", "0.1"))  # Minimum delay between messages (seconds)
MAX_SEND_DELAY = float(os.getenv("MAX_SEND_DELAY", "2.0"))  # Maximum delay between messages
BATCH_SEND_ENABLED = os.getenv("BATCH_SEND_ENABLED", "False").lower() in ("true", "1", "yes")  # Enable batch sending

# Performance
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))  # Task timeout in seconds
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # Flask request timeout
