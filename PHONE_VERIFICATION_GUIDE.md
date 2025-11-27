# Phone Verification Feature - Documentation

## Overview

This feature ensures that all users must share their phone number before they can interact with the bot. When a user sends any message without having their phone number saved, the bot automatically requests it using a contact button.

## How It Works

### User Flow

1. **New User Sends Message**
   - User sends any message or `/start` command
   - Bot checks if phone number exists in database
   - If not found, bot sends a request with a button

2. **Phone Number Request**
   - Bot displays: "مرحباً! 👋 للمتابعة، يرجى مشاركة رقم هاتفك معنا"
   - Shows button: "مشاركة رقم الهاتف" (request_contact=True)
   - User clicks button to share their contact

3. **Phone Number Saved**
   - Bot validates the contact is user's own number
   - Saves phone number to MongoDB
   - Sends confirmation: "✅ شكراً! تم حفظ رقم هاتفك"
   - Shows welcome message
   - Removes keyboard

4. **Subsequent Messages**
   - Phone number check passes
   - User can interact normally with the bot

### Security Features

- ✅ **Validation**: Ensures user shares their own phone number, not someone else's
- ✅ **No Duplicates**: Uses MongoDB update operations to prevent duplicate entries
- ✅ **Error Handling**: Comprehensive try-catch blocks with logging
- ✅ **Database Integrity**: Phone number stored with verification timestamp

## Database Schema

### User Document Structure

```javascript
{
  "chat_id": 123456789,              // Telegram user ID (unique index)
  "name": "Ahmed",                    // User's first name
  "phone_number": "+201234567890",    // Phone number (null if not shared)
  "phone_verified_at": ISODate(),     // Timestamp when phone was saved
  "joined_at": ISODate(),             // First interaction timestamp
  "updated_at": ISODate(),            // Last update timestamp
  "last_activity_at": ISODate(),      // Last activity timestamp
  "last_activity_type": "message",    // Type of last activity
  "message_count": 5,                 // Total messages sent
  "status": "active"                  // User status
}
```

## Code Structure

### 1. Database Methods (`database.py`)

#### `has_phone_number(chat_id: int) -> bool`
- Checks if user has a phone number saved
- Returns `True` if phone exists and is not None
- Returns `False` otherwise

#### `save_phone_number(chat_id: int, phone_number: str)`
- Saves user's phone number
- Updates `phone_verified_at` timestamp
- Logs success/failure

#### `get_user_phone(chat_id: int) -> str`
- Retrieves user's phone number
- Returns phone string or None

### 2. Bot Handlers (`bot_handler.py`)

#### `request_phone_number(chat_id)`
- Creates ReplyKeyboardMarkup with contact button
- Button text: "مشاركة رقم الهاتف"
- Sets `request_contact=True`
- Sends message in Arabic

#### `phone_required` (Decorator)
- Wraps message handlers
- Checks if user has phone number
- If not: requests phone and stops handler execution
- If yes: proceeds with original handler

#### `handle_contact(message)`
- Handles contact sharing (content_type='contact')
- Validates contact is user's own number
- Saves to database
- Sends confirmation
- Removes keyboard

#### `on_start(message)` & `on_message(message)`
- Both decorated with `@phone_required`
- Only execute if user has shared phone number

## Testing the Feature

### Test Case 1: New User
1. Open Telegram and find your bot
2. Send any message (e.g., "Hello")
3. **Expected**: Bot asks for phone number with button
4. Click "مشاركة رقم الهاتف"
5. **Expected**: Confirmation message with phone number
6. Send another message
7. **Expected**: Normal bot response (welcome message)

### Test Case 2: Existing User with Phone
1. User who already shared phone sends message
2. **Expected**: Bot responds normally without requesting phone

### Test Case 3: Wrong Contact Shared
1. New user sends message
2. Bot requests phone
3. User shares someone else's contact
4. **Expected**: Warning message + phone request again

### Test Case 4: Database Persistence
1. User shares phone number
2. Stop and restart bot
3. User sends message
4. **Expected**: Bot responds normally (phone still saved)

## MongoDB Queries for Admin

### Check users without phone numbers
```javascript
db.users.find({ phone_number: null })
```

### Count users with phone numbers
```javascript
db.users.countDocuments({ phone_number: { $ne: null } })
```

### Find user by phone number
```javascript
db.users.findOne({ phone_number: "+201234567890" })
```

### Get all phone numbers
```javascript
db.users.find(
  { phone_number: { $ne: null } },
  { chat_id: 1, name: 1, phone_number: 1, _id: 0 }
)
```

## Error Handling

### Database Errors
- All database operations wrapped in try-catch
- Errors logged with user context
- User receives friendly error message in Arabic

### Contact Validation Errors
- Checks if `message.contact.user_id == message.from_user.id`
- Prevents sharing other people's contacts
- Re-requests phone if validation fails

### Network Errors
- Bot polling has auto-restart mechanism
- Database connection has retry logic
- All failures logged for debugging

## Configuration

### Environment Variables
No additional environment variables needed. The feature uses existing:
- `MONGODB_URI`: MongoDB connection string
- `TELEGRAM_TOKEN`: Bot token
- `WELCOME_MESSAGE`: Message shown after phone verification

### Customization

To customize the phone request message, edit in `bot_handler.py`:
```python
message_text = (
    "مرحباً! 👋\n\n"
    "للمتابعة، يرجى مشاركة رقم هاتفك معنا.\n"
    "اضغط على الزر أدناه لمشاركة رقمك."
)
```

To customize the button text:
```python
contact_button = types.KeyboardButton(text="مشاركة رقم الهاتف", request_contact=True)
```

## Deployment Notes

### Railway Deployment
1. The feature works automatically on Railway
2. No additional dependencies required (uses existing `pyTelegramBotAPI`)
3. MongoDB must be accessible from Railway

### Local Testing
1. Ensure MongoDB is running locally or use MongoDB Atlas
2. Update `.env` with correct `MONGODB_URI`
3. Run: `python main.py` or `python app.py`

## Troubleshooting

### Issue: Phone request not showing
- **Check**: Bot has permission to send messages
- **Check**: User hasn't blocked the bot
- **Check**: Database connection is working

### Issue: Phone number not saving
- **Check**: MongoDB connection string is correct
- **Check**: Database has write permissions
- **Check**: Logs for error messages

### Issue: Button not appearing
- **Check**: Using correct Telegram client (some old clients don't support contact buttons)
- **Check**: `request_contact=True` is set on KeyboardButton

### Issue: Decorator not working
- **Check**: `@phone_required` is placed AFTER `@bot.message_handler`
- **Check**: Import `from functools import wraps` exists

## Best Practices

1. **Privacy**: Only request phone when necessary
2. **Logging**: All phone operations are logged for audit
3. **Validation**: Always validate contact belongs to user
4. **User Experience**: Clear Arabic messages for Egyptian users
5. **Error Messages**: Friendly, actionable error messages

## Future Enhancements

Potential improvements:
- [ ] Add phone number verification via SMS OTP
- [ ] Allow users to update their phone number
- [ ] Add admin command to view users without phone numbers
- [ ] Export phone numbers to Excel
- [ ] Phone number formatting/validation
- [ ] Multi-language support

## Support

For issues or questions:
1. Check logs in `app.log` or `data/app.log`
2. Verify MongoDB connection
3. Test with a fresh user account
4. Check Telegram Bot API status

---

**Last Updated**: 2025-11-27  
**Version**: 1.0  
**Author**: Telegram Bot Admin System
