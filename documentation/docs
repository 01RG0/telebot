# Quick Reference Guide

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
copy .env.example .env

# 3. Edit .env with your settings
# - Add your TELEGRAM_TOKEN
# - Add your MONGODB_URI

# 4. Run the application
python main.py
```

### Using start.bat (Windows)
```bash
# Double-click start.bat or run:
start.bat
```

## 📝 Configuration (.env file)

```env
# Required
TELEGRAM_TOKEN=your_bot_token_from_botfather
MONGODB_URI=mongodb://localhost:27017/

# Optional
DATABASE_NAME=telegram_bot
SEND_DELAY=0.5
LOG_LEVEL=INFO
```

## 🗄️ MongoDB Connection Strings

### Local MongoDB
```
MONGODB_URI=mongodb://localhost:27017/
```

### MongoDB Atlas (Free Cloud)
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### MongoDB with Authentication
```
MONGODB_URI=mongodb://username:password@localhost:27017/
```

## 📂 File Purposes

| File | Purpose |
|------|---------|
| `main.py` | Start the application |
| `config.py` | Configuration settings |
| `database.py` | MongoDB operations |
| `bot_handler.py` | Telegram bot logic |
| `gui.py` | Admin GUI interface |
| `migrate_to_mongodb.py` | Migrate from SQLite |
| `start.bat` | Quick start script |

## 🎯 Common Tasks

### Send Message to All Users
1. Open GUI
2. Click "Select All"
3. Enter message in template field
4. Click "Send to Selected"

### Send Personalized Messages
1. Create Excel file:
   - Column A: chat_id or name
   - Column B: message
2. Click "Load Excel"
3. Click "Send Imported Rows"

### Export User List
1. Click "Export users"
2. Choose CSV or Excel
3. Save file

### Search Users
- Type in search box
- Searches both name and chat_id

### Delete User
- Click "Delete" button next to user
- Confirm deletion

## 🔧 Troubleshooting

### Bot Not Working
```bash
# Check logs
type app.log

# Verify token
# Open .env and check TELEGRAM_TOKEN
```

### Database Connection Error
```bash
# Test MongoDB connection
# For local: Make sure MongoDB is running
# For Atlas: Check connection string and password
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### GUI Not Opening
```bash
# Install CustomTkinter
pip install customtkinter

# Check Python version (need 3.8+)
python --version
```

## 📊 Excel Import Format

### Template for Personalized Messages

| A (target) | B (message) |
|------------|-------------|
| 123456789 | Hello! Your custom message here |
| John Smith | Hi John, this is for you |
| 987654321 | Another personalized message |

**Notes**:
- Column A can be chat_id (number) or name (text)
- Column B is the message text
- Empty rows are skipped

## 🔐 Security Checklist

- [ ] Created .env file (not .env.example)
- [ ] Added .env to .gitignore
- [ ] Never commit .env to git
- [ ] Use strong MongoDB password
- [ ] Whitelist IPs in MongoDB Atlas
- [ ] Keep bot token secret
- [ ] Regular database backups

## 📱 Getting Bot Token

1. Open Telegram
2. Search for [@BotFather](https://t.me/botfather)
3. Send `/newbot`
4. Follow instructions
5. Copy the token
6. Add to .env file

## 🌐 MongoDB Atlas Setup

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create cluster (free tier)
4. Create database user
5. Whitelist IP (0.0.0.0/0 for testing)
6. Get connection string
7. Replace `<password>` with your password
8. Add to .env file

## 🔄 Migration from Old bot.py

```bash
# If you have users.db from old version
python migrate_to_mongodb.py

# Follow prompts to migrate users
```

## 📋 Message Template Variables

Use these in your message templates:

- `{name}` - User's first name
- `{chat_id}` - User's chat ID

Example:
```
Hello {name}! Your ID is {chat_id}
```

## 🐛 Debug Mode

To enable detailed logging:

```env
# In .env file
LOG_LEVEL=DEBUG
```

Then check `app.log` for detailed information.

## 📞 Support Commands

### Check Logs
```bash
# Windows
type app.log

# View last 50 lines
powershell -command "Get-Content app.log -Tail 50"
```

### Clear Logs
```bash
# Windows
del app.log
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## ⚡ Performance Tips

1. **Adjust Send Delay**: 
   - Default: 0.5 seconds
   - Faster: 0.3 seconds (risky)
   - Safer: 1.0 seconds

2. **Database Indexes**: 
   - Automatically created on first run
   - Improves search performance

3. **Connection Pooling**:
   - MongoDB handles automatically
   - No configuration needed

## 🎨 Customization

### Change Welcome Message
```env
# In .env file
WELCOME_MESSAGE=Your custom welcome message here
```

### Change Window Size
Edit `config.py`:
```python
WINDOW_SIZE = "1200x800"  # Width x Height
```

### Change Send Delay
```env
# In .env file
SEND_DELAY=1.0  # seconds
```

## 📦 Project Structure

```
telebot/
├── main.py              ← Start here
├── config.py            ← Configuration
├── database.py          ← MongoDB
├── bot_handler.py       ← Bot logic
├── gui.py               ← Admin GUI
├── requirements.txt     ← Dependencies
├── .env                 ← Your settings (create this)
├── .env.example         ← Template
├── start.bat            ← Quick start
├── migrate_to_mongodb.py ← Migration tool
├── README.md            ← Full documentation
└── REFACTORING_SUMMARY.md ← Technical details
```

## 🎓 Learning Resources

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Python dotenv](https://pypi.org/project/python-dotenv/)
- [CustomTkinter](https://customtkinter.tomschimansky.com/)

## ✅ Pre-flight Checklist

Before running:
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created and configured
- [ ] MongoDB running (local) or Atlas configured
- [ ] Bot token obtained from BotFather
- [ ] Bot token added to .env

## 🚨 Emergency Procedures

### Bot Compromised
1. Go to [@BotFather](https://t.me/botfather)
2. Send `/mybots`
3. Select your bot
4. Click "API Token"
5. Click "Revoke current token"
6. Get new token
7. Update .env file

### Database Corrupted
1. Stop application
2. Restore from backup
3. Or create new database
4. Users will need to re-register

### Lost .env File
1. Copy .env.example to .env
2. Add your bot token
3. Add MongoDB connection string
4. Restart application

---

**Need more help?** Check `README.md` for detailed documentation.
