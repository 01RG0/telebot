"""
Optimized message sending functions with progress tracking and batching
"""
import time
import logging
from typing import List, Dict, Callable, Optional
from config import SEND_DELAY
from database import db
from bot_handler import bot

logger = logging.getLogger("message_sender")


def send_personalized_from_template_optimized(
    template: str,
    rows: List[Dict],
    delay: float = SEND_DELAY,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Send personalized messages using a template and data from rows
    Optimized version with progress tracking
    
    Args:
        template: Message template string with {column_name} placeholders
        rows: List of dicts with "target" and other data columns
        delay: Delay between sends in seconds
        progress_callback: Optional callback(current_index, total) for progress tracking
        
    Returns:
        Dict with 'sent', 'failed', 'total', and 'failed_details'
    """
    sent = []
    failed = []
    total_rows = len(rows)
    
    for idx, row in enumerate(rows):
        target = row.get("target")
        
        if not target:
            failed.append((target, "Missing target"))
            if progress_callback:
                progress_callback(idx + 1, total_rows)
            continue

        # Format message using template and row data
        try:
            message = template.format(**row)
        except KeyError as e:
            failed.append((target, f"Missing placeholder data: {e}"))
            if progress_callback:
                progress_callback(idx + 1, total_rows)
            continue

        # If target is numeric → treat as chat_id
        if isinstance(target, (int,)) or (isinstance(target, str) and target.isdigit()):
            cid = int(target)
            try:
                bot.send_message(cid, message)
                sent.append(cid)
                logger.info(f"Sent message to {cid}")
            except Exception as e:
                failed.append((cid, str(e)))
                logger.warning(f"Failed to send to {cid}: {e}")
        else:
            # Treat as name search
            matches = db.find_users_by_name(str(target))
            if not matches:
                failed.append((target, "no matching user by name"))
            else:
                # Send to all matches
                for cid, name in matches:
                    try:
                        bot.send_message(cid, message)
                        sent.append(cid)
                        logger.info(f"Sent message to {cid} ({name})")
                    except Exception as e:
                        failed.append((cid, str(e)))
                        logger.warning(f"Failed to send to {cid}: {e}")
        
        # Sleep with delay
        time.sleep(delay)
        
        # Call progress callback
        if progress_callback:
            progress_callback(idx + 1, total_rows)
    
    return {
        'sent': len(sent),
        'failed': len(failed),
        'total': total_rows,
        'failed_details': failed[:10]  # Keep first 10 failures
    }


def send_bulk_optimized(
    chat_ids: List[int],
    message: str,
    delay: float = SEND_DELAY,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Send the same message to multiple chat IDs
    Optimized version with progress tracking
    
    Args:
        chat_ids: List of chat IDs
        message: Message text
        delay: Delay between sends in seconds
        progress_callback: Optional callback(current_index, total) for progress tracking
        
    Returns:
        Dict with 'sent', 'failed', 'total', and 'failed_details'
    """
    sent = []
    failed = []
    total_ids = len(chat_ids)
    
    for idx, cid in enumerate(chat_ids):
        try:
            bot.send_message(cid, message)
            sent.append(cid)
            logger.info(f"Sent message to {cid}")
        except Exception as e:
            failed.append((cid, str(e)))
            logger.warning(f"Failed to send to {cid}: {e}")
        
        # Sleep with delay
        time.sleep(delay)
        
        # Call progress callback
        if progress_callback:
            progress_callback(idx + 1, total_ids)
    
    return {
        'sent': len(sent),
        'failed': len(failed),
        'total': total_ids,
        'failed_details': failed[:10]
    }


def send_template_to_selected_optimized(
    chat_ids: List[int],
    template: str,
    delay: float = SEND_DELAY,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Send templated message to specific chat IDs
    Optimized version with progress tracking
    
    Args:
        chat_ids: List of chat IDs
        template: Message template
        delay: Delay between sends in seconds
        progress_callback: Optional callback(current_index, total) for progress tracking
        
    Returns:
        Dict with 'sent', 'failed', 'total', and 'failed_details'
    """
    sent = []
    failed = []
    total_ids = len(chat_ids)
    
    for idx, cid in enumerate(chat_ids):
        try:
            bot.send_message(cid, template)
            sent.append(cid)
            logger.info(f"Sent template message to {cid}")
        except Exception as e:
            failed.append((cid, str(e)))
            logger.warning(f"Failed to send to {cid}: {e}")
        
        # Sleep with delay
        time.sleep(delay)
        
        # Call progress callback
        if progress_callback:
            progress_callback(idx + 1, total_ids)
    
    return {
        'sent': len(sent),
        'failed': len(failed),
        'total': total_ids,
        'failed_details': failed[:10]
    }
