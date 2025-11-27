"""
Telegram bot handlers and message processing
"""
import telebot
from telebot import types
import logging
import time
import re
from functools import wraps
from config import TELEGRAM_TOKEN, WELCOME_MESSAGE, SEND_DELAY
from database import db

logger = logging.getLogger("telegram_app.bot")

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")


def request_phone_number(chat_id):
    """
    Send a message requesting phone number with an inline button
    
    Args:
        chat_id: Telegram chat ID
    """
    try:
        # Create inline keyboard with button
        keyboard = types.InlineKeyboardMarkup()
        phone_button = types.InlineKeyboardButton(
            text="📱 مشاركة رقم الهاتف",
            callback_data="request_phone"
        )
        keyboard.add(phone_button)
        
        message_text = (
            "مرحباً! 👋\n\n"
            "للمتابعة، يرجى مشاركة رقم هاتفك معنا.\n\n"
            "اضغط على الزر أدناه ثم أرسل رقم هاتفك.\n"
            "مثال: +201234567890"
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


@bot.callback_query_handler(func=lambda call: call.data == "request_phone")
def handle_phone_button_click(call):
    """
    Handle inline button click for phone number request
    """
    try:
        chat_id = call.message.chat.id
        
        # Answer the callback to remove loading state
        bot.answer_callback_query(call.id)
        
        # Add user to tracking set
        users_sharing_phone.add(chat_id)
        
        # Edit the message to show instructions
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=(
                "📱 *مشاركة رقم الهاتف*\n\n"
                "الآن، يرجى إرسال رقم هاتفك.\n\n"
                "يجب أن يبدأ الرقم بـ + ورمز الدولة\n"
                "مثال: +201234567890\n\n"
                "أرسل رقمك الآن 👇"
            ),
            parse_mode="Markdown"
        )
        
        logger.info(f"User {chat_id} clicked phone request button")
    except Exception as e:
        logger.exception(f"Error handling phone button click: {e}")


# Track users who are in the process of sharing phone
users_sharing_phone = set()


@bot.message_handler(func=lambda m: m.chat.id in users_sharing_phone and m.content_type == 'text')
def handle_manual_phone_input(message):
    """
    Handle manual phone number input from users
    """
    try:
        chat_id = message.chat.id
        phone_text = message.text.strip()
        name = message.from_user.first_name or ""
        
        # Basic phone validation (starts with + and contains 10-15 digits)
        if re.match(r'^\+\d{10,15}$', phone_text):
            # Valid phone format
            db.add_or_update_user(chat_id, name, "phone_shared")
            db.save_phone_number(chat_id, phone_text)
            
            # Remove from tracking set
            users_sharing_phone.discard(chat_id)
            
            # Send confirmation
            bot.send_message(
                chat_id,
                f"✅ شكراً! تم حفظ رقم هاتفك: {phone_text}\n\n{WELCOME_MESSAGE}"
            )
            logger.info(f"Phone number saved for user {chat_id}: {phone_text}")
        else:
            # Invalid format
            bot.send_message(
                chat_id,
                "❌ رقم الهاتف غير صحيح!\n\n"
                "يجب أن يبدأ بـ + ورمز الدولة\n"
                "مثال: +201234567890\n\n"
                "يرجى المحاولة مرة أخرى:"
            )
    except Exception as e:
        logger.exception(f"Error handling manual phone input: {e}")
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
