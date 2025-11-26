"""
Telegram bot handlers and message processing
"""
import telebot
import logging
import time
from config import TELEGRAM_TOKEN, WELCOME_MESSAGE, SEND_DELAY
from database import db

logger = logging.getLogger("telegram_app.bot")

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def on_start(message):
    """Handle /start command"""
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        db.add_or_update_user(chat_id, name)
        bot.send_message(chat_id, WELCOME_MESSAGE)
        logger.info(f"New/updated user: {chat_id} | {name}")
    except Exception as e:
        logger.exception(f"Error in /start handler: {e}")


@bot.message_handler(func=lambda m: True)
def on_message(message):
    """
    Handle all other messages
    Store chat_id + name on any message
    """
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        db.add_or_update_user(chat_id, name)
        bot.send_message(chat_id, WELCOME_MESSAGE)
    except Exception as e:
        logger.exception(f"Error in message handler: {e}")


def run_bot_forever():
    """Run bot with resilient polling loop"""
    while True:
        try:
            logger.info("Starting bot polling...")
            bot.infinity_polling(timeout=30, long_polling_timeout=60)
        except Exception as e:
            logger.exception(f"Bot polling crashed, restarting: {e}")
            time.sleep(5)


def safe_send_message(chat_id, text):
    """
    Safely send a message to a chat
    
    Args:
        chat_id: Telegram chat ID
        text: Message text
        
    Returns:
        Tuple (success: bool, error: str or None)
    """
    try:
        bot.send_message(chat_id, text)
        logger.info(f"Sent to {chat_id}")
        return True, None
    except Exception as e:
        logger.exception(f"Failed to send to {chat_id}: {e}")
        return False, str(e)


def send_bulk_by_chatids(chat_ids, message, delay=SEND_DELAY):
    """
    Send the same message to multiple chat IDs
    
    Args:
        chat_ids: List of chat IDs
        message: Message text
        delay: Delay between sends in seconds
        
    Returns:
        Tuple (sent: list, failed: list)
    """
    sent, failed = [], []
    for cid in chat_ids:
        ok, err = safe_send_message(cid, message)
        if ok:
            sent.append(cid)
        else:
            failed.append((cid, err))
        time.sleep(delay)
    return sent, failed


def send_template_to_selected(chat_ids, template, delay=SEND_DELAY):
    """
    Send templated messages to selected users
    Template can use {name} and {chat_id} placeholders
    
    Args:
        chat_ids: List of chat IDs
        template: Message template string
        delay: Delay between sends in seconds
        
    Returns:
        Tuple (sent: list, failed: list)
    """
    sent, failed = [], []
    for cid in chat_ids:
        user = db.get_user_by_chat(cid)
        name = user[1] if user else ""
        try:
            msg = template.format(name=name or "", chat_id=cid)
        except Exception:
            msg = template
        ok, err = safe_send_message(cid, msg)
        if ok:
            sent.append(cid)
        else:
            failed.append((cid, err))
        time.sleep(delay)
    return sent, failed


def send_personalized_from_rows(rows, delay=SEND_DELAY):
    """
    Send personalized messages from imported rows
    
    Args:
        rows: List of dicts {"target": <chat_id or name>, "message": <text>}
        delay: Delay between sends in seconds
        
    Returns:
        Tuple (sent: list, failed: list)
    """
    sent, failed = [], []
    for r in rows:
        target = r.get("target")
        message = r.get("message", "")
        
        # If target is numeric → treat as chat_id
        if isinstance(target, (int,)) or (isinstance(target, str) and target.isdigit()):
            cid = int(target)
            ok, err = safe_send_message(cid, message)
            if ok:
                sent.append(cid)
            else:
                failed.append((cid, err))
        else:
            # Treat as name search
            matches = db.find_users_by_name(str(target))
            if not matches:
                failed.append((target, "no matching user by name"))
            else:
                # Send to all matches
                for cid, name in matches:
                    ok, err = safe_send_message(cid, message)
                    if ok:
                        sent.append(cid)
                    else:
                        failed.append((cid, err))
        time.sleep(delay)
    return sent, failed
