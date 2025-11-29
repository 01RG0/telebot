"""
Telegram bot handlers and message processing
"""
import telebot
from telebot import types
import logging
import time
from functools import wraps
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import TELEGRAM_TOKEN, WELCOME_MESSAGE, SEND_DELAY
from database import db

logger = logging.getLogger("telegram_app.bot")

# Initialize bot with resilient connection settings
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")

# Configure session with retry strategy for better connection handling
session = bot.session
adapter = HTTPAdapter(
    max_retries=Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "POST"]
    ),
    pool_connections=10,
    pool_maxsize=10
)
session.mount('http://', adapter)
session.mount('https://', adapter)


def request_phone_number(chat_id):
    """
    Send welcome message with phone number request button
    
    Args:
        chat_id: Telegram chat ID
    """
    try:
        # Create keyboard with contact request button
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        contact_button = types.KeyboardButton(text="📱 مشاركة رقم الهاتف", request_contact=True)
        keyboard.add(contact_button)
        
        # Combine welcome message with phone request
        message_text = (
            f"{WELCOME_MESSAGE}\n\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 للمتابعة، يرجى الضغط على مشاركة رقم هاتفك معنا.\n"
            "اضغط على الزر أدناه لمشاركة رقمك تلقائياً."
        )
        
        bot.send_message(chat_id, message_text, reply_markup=keyboard)
        logger.info(f"Phone number request sent to user {chat_id}")
    except Exception as e:
        logger.error(f"Failed to request phone number from {chat_id}: {e}")


def phone_required(handler_func):
    """
    Decorator to check if user has phone number before processing
    If not, request phone number and skip handler
    """
    @wraps(handler_func)
    def wrapper(message):
        chat_id = message.chat.id
        
        # Check if user has phone number
        if not db.has_phone_number(chat_id):
            # Ensure user exists in database first
            name = message.from_user.first_name or ""
            db.add_or_update_user(chat_id, name, "message")
            
            # Request phone number
            request_phone_number(chat_id)
            return  # Don't process the original handler
        
        # User has phone number, proceed with handler
        return handler_func(message)
    
    return wrapper


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    """
    Handle contact sharing (phone number)
    Save phone number to database
    """
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        
        # Ensure user exists in database
        db.add_or_update_user(chat_id, name, "contact_shared")
        
        # Check if contact is user's own phone number
        if message.contact.user_id == message.from_user.id:
            phone_number = message.contact.phone_number
            
            # Save phone number
            db.save_phone_number(chat_id, phone_number)
            
            # Remove keyboard and send confirmation
            remove_keyboard = types.ReplyKeyboardRemove()
            confirmation_text = (
                f"✅ تم بنجاح!\n\n"
                f"تم حفظ رقم هاتفك: {phone_number}\n\n"
                f"يمكنك الآن استخدام البوت بشكل طبيعي. 🎉"
            )
            bot.send_message(
                chat_id,
                confirmation_text,
                reply_markup=remove_keyboard
            )
            logger.info(f"Phone number saved for user {chat_id}: {phone_number}")
        else:
            # User shared someone else's contact
            bot.send_message(
                chat_id,
                "⚠️ يرجى مشاركة رقم هاتفك الشخصي، وليس رقم شخص آخر."
            )
            request_phone_number(chat_id)
            
    except Exception as e:
        logger.exception(f"Error handling contact from {chat_id}: {e}")
        bot.send_message(chat_id, "حدث خطأ أثناء حفظ رقم هاتفك. يرجى المحاولة مرة أخرى.")


@bot.message_handler(commands=["start"])
@phone_required
def on_start(message):
    """Handle /start command - requires phone number"""
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        db.add_or_update_user(chat_id, name, "start")
        bot.send_message(chat_id, WELCOME_MESSAGE)
        logger.info(f"New/updated user: {chat_id} | {name}")
    except Exception as e:
        logger.exception(f"Error in /start handler: {e}")


@bot.message_handler(func=lambda m: True)
@phone_required
def on_message(message):
    """
    Handle all other messages - requires phone number
    Store chat_id + name on any message
    """
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        db.add_or_update_user(chat_id, name, "message")
        bot.send_message(chat_id, WELCOME_MESSAGE)
    except Exception as e:
        logger.exception(f"Error in message handler: {e}")



def run_bot_forever():
    """Run bot with resilient polling loop and connection retry logic"""
    retry_count = 0
    max_retries = 10
    base_backoff = 5
    
    while True:
        try:
            logger.info(f"Starting bot polling... (retry: {retry_count})")
            # Reset retry count on successful connection
            retry_count = 0
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=60,
                skip_pending=True,
                allowed_updates=None
            )
        except ConnectionError as e:
            # Handle connection errors with exponential backoff
            retry_count = min(retry_count + 1, max_retries)
            backoff_time = base_backoff * (2 ** (retry_count - 1))
            logger.error(f"Connection error (attempt {retry_count}/{max_retries}): {e}")
            logger.info(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
        except Exception as e:
            # Handle other exceptions
            if "RemoteDisconnected" in str(type(e)):
                retry_count = min(retry_count + 1, max_retries)
                backoff_time = base_backoff * (2 ** (retry_count - 1))
                logger.error(f"Remote disconnected (attempt {retry_count}/{max_retries}): {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                logger.exception(f"Bot polling crashed: {e}")
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


def send_personalized_from_template(template, rows, delay=SEND_DELAY):
    """
    Send personalized messages using a template and data from rows

    Args:
        template: Message template string with {column_name} placeholders
        rows: List of dicts with "target" and other data columns
        delay: Delay between sends in seconds

    Returns:
        Tuple (sent: list, failed: list)
    """
    sent, failed = [], []
    for r in rows:
        target = r.get("target")
        if not target:
            failed.append((target, "Missing target"))
            continue

        # Format message using template and row data
        try:
            message = template.format(**r)
        except KeyError as e:
            failed.append((target, f"Missing placeholder data: {e}"))
            continue

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
