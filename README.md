# Telegram Bot Admin System

A comprehensive Telegram bot administration system with MongoDB support, featuring a GUI admin panel for managing users and sending bulk/personalized messages.

## Features

- 🤖 **Telegram Bot Integration**: Automatic user registration and welcome messages
- 💾 **MongoDB Database**: Flexible NoSQL database with connection string support
- 🖥️ **Admin GUI**: Modern CustomTkinter-based interface for managing users
- 📤 **Bulk Messaging**: Send messages to multiple users at once
- 📝 **Template Messages**: Use placeholders like `{name}` and `{chat_id}` in messages
- 📊 **Excel Import/Export**: Import personalized messages from Excel, export user lists
- 🔍 **Search & Filter**: Easily find users by name or chat ID
- 🔐 **Environment Variables**: Secure configuration using .env files

## Project Structure

```
telebot/
├── main.py              # Application entry point
├── config.py            # Configuration and environment variables
├── database.py          # MongoDB database operations
├── bot_handler.py       # Telegram bot handlers and messaging
├── gui.py               # Admin GUI interface
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment configuration
├── .env                 # Your actual configuration (create this)
└── README.md           # This file
```

## Installation

### 1. Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas account)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### 2. Clone or Download

```bash
cd c:\Users\ahmed\Desktop\telebot\telebot
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` file with your settings:

```env
# Your Telegram Bot Token
TELEGRAM_TOKEN=your_bot_token_here

# MongoDB Connection String
# For local MongoDB:
MONGODB_URI=mongodb://localhost:27017/

# For MongoDB Atlas (cloud):
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Database Name
DATABASE_NAME=telegram_bot

# Application Settings
SEND_DELAY=0.5
WELCOME_MESSAGE=اهلا بيك في نظام المتابعة لمستر شادي الشرقاوي شكرا على ثقتك بنتمنى نكون عند حسن ظنك
```

## MongoDB Setup

### Option 1: Local MongoDB

1. Install MongoDB Community Edition from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Start MongoDB service
3. Use connection string: `mongodb://localhost:27017/`

### Option 2: MongoDB Atlas (Cloud)

1. Create free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Get your connection string from "Connect" → "Connect your application"
4. Replace `<password>` with your database user password
5. Use the connection string in your `.env` file

Example Atlas connection string:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

## Usage

### Running the Application

```bash
python main.py
```

This will:
1. Connect to MongoDB
2. Start the Telegram bot in the background
3. Launch the admin GUI

### Admin GUI Features

#### User Management
- **Search**: Type in the search box to filter users by name or chat ID
- **Refresh**: Update the user list from the database
- **Select All/Deselect All**: Quickly select or deselect all users
- **Delete**: Remove users from the database

#### Sending Messages

1. **Template Messages to Selected Users**:
   - Select users using checkboxes
   - Enter a message template (use `{name}` or `{chat_id}` as placeholders)
   - Click "Send to Selected"

2. **Personalized Messages from Excel**:
   - Prepare an Excel file with:
     - Column A: Target (chat_id or name)
     - Column B: Message text
   - Click "Load Excel (A=target, B=message)"
   - Click "Send Imported Rows"

#### Export Users
- Click "Export users"
- Choose CSV or Excel format
- Save the file

### Excel Import Format

Create an Excel file with this structure:

| A (target) | B (message) |
|------------|-------------|
| 123456789  | Hello User 1! |
| John       | Hi John, this is your message |
| 987654321  | Custom message for this user |

- **Column A**: Can be either chat_id (numeric) or user name (text)
- **Column B**: The message to send to that user

## Bot Commands

Users can interact with your bot using:

- `/start` - Register and receive welcome message
- Any message - Will trigger registration and welcome message

## Configuration Options

All configuration is in `config.py` and can be overridden with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Your bot token from BotFather | Required |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `DATABASE_NAME` | Database name | `telegram_bot` |
| `SEND_DELAY` | Delay between messages (seconds) | `0.5` |
| `WELCOME_MESSAGE` | Message sent to new users | Arabic welcome message |
| `LOG_FILE` | Log file path | `app.log` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Logging

All application activity is logged to `app.log` including:
- User registrations
- Message sending (success/failure)
- Database operations
- Errors and exceptions

## Migration from SQLite

If you're migrating from the old `bot.py` with SQLite:

1. The old `users.db` SQLite file is no longer used
2. Users will need to re-register with the bot (send `/start`)
3. Alternatively, you can write a migration script to transfer data from SQLite to MongoDB

## Troubleshooting

### Bot not responding
- Check your `TELEGRAM_TOKEN` in `.env`
- Verify internet connection
- Check `app.log` for errors

### Database connection failed
- Verify MongoDB is running (for local setup)
- Check `MONGODB_URI` connection string
- For Atlas: Verify IP whitelist and credentials

### GUI not opening
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if CustomTkinter is properly installed

### Messages not sending
- Check `app.log` for specific errors
- Verify users have started the bot (sent `/start`)
- Ensure `SEND_DELAY` is not too low (minimum 0.5 recommended)

## Security Notes

⚠️ **Important Security Practices**:

1. **Never commit `.env` file** to version control
2. **Keep your bot token secret** - regenerate if exposed
3. **Use strong passwords** for MongoDB Atlas
4. **Whitelist specific IPs** in MongoDB Atlas (not 0.0.0.0/0)
5. **Regularly backup** your MongoDB database

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the logs in `app.log`
2. Review this README
3. Verify your configuration in `.env`

---

**Made with ❤️ for Mr. Shady's Telegram Administration System**
