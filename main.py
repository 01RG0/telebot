"""
Main entry point for the Telegram bot application
"""
import threading
import logging
from config import LOG_FILE, LOG_LEVEL
from database import db
from bot_handler import bot, run_bot_forever
from legacy_code.gui import AdminApp

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telegram_app")


def main():
    """Main application entry point"""
    logger.info("=" * 50)
    logger.info("Starting Telegram Admin Application")
    logger.info("=" * 50)
    
    # Test bot connection (non-blocking)
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot connected successfully: @{bot_info.username}")
    except Exception as e:
        logger.warning(f"bot.get_me() failed (may be okay if network blocked): {e}")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot_forever, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")
    
    # Start GUI (main thread)
    try:
        logger.info("Starting GUI application")
        app = AdminApp()
        app.mainloop()
    except Exception as e:
        logger.exception(f"GUI crashed: {e}")
    finally:
        # Cleanup
        logger.info("Shutting down application")
        db.close()


if __name__ == "__main__":
    main()
