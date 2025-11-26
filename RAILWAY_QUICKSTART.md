# Railway Deployment - Quick Start

## ✅ Your Project is Railway-Ready!

### 📦 What's Been Added for Railway:

| File | Purpose |
|------|---------|
| `bot_only.py` | Headless bot (no GUI) for server deployment |
| `Procfile` | Tells Railway how to start your app |
| `railway.json` | Railway configuration |
| `runtime.txt` | Python version specification |
| `.railwayignore` | Files to exclude from deployment |

### 🚀 Deploy in 3 Steps:

#### 1️⃣ Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2️⃣ Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables (see below)

#### 3️⃣ Add Environment Variables in Railway
```
TELEGRAM_TOKEN=8334074221:AAE8pGbyawYLnZmDlQd4fRXoW0p0hvO7koY
MONGODB_URI=mongodb+srv://root:root@cluster0.xzdok6x.mongodb.net/?appName=Cluster0
DATABASE_NAME=telegram_bot
SEND_DELAY=0.5
LOG_LEVEL=INFO
```

### ✅ That's It!

Railway will:
- ✅ Install dependencies
- ✅ Start `bot_only.py`
- ✅ Run your bot 24/7
- ✅ Auto-restart if it crashes

### 🧪 Test Locally First (Optional)

Test the headless version before deploying:
```bash
python bot_only.py
```

This runs the same code Railway will run (no GUI).

### 📱 How It Works

**On Railway (Cloud):**
- Bot runs 24/7
- Users interact via Telegram
- Data stored in MongoDB Atlas

**On Your PC (Local):**
- Run `python main.py` for admin GUI
- Manage users
- Send bulk messages
- Same MongoDB database

### 🔧 MongoDB Atlas Setup

Make sure MongoDB Atlas allows Railway connections:
1. Go to MongoDB Atlas
2. Network Access → Add IP Address
3. Allow access from anywhere: `0.0.0.0/0`
4. Save

### 📊 After Deployment

**Check Railway Logs:**
- Look for: "Bot connected successfully"
- Look for: "MongoDB connected successfully"
- Look for: "Bot is now running"

**Test Your Bot:**
- Open Telegram
- Send `/start` to your bot
- Should receive welcome message

### 🎯 Full Guide

See `RAILWAY_DEPLOYMENT.md` for detailed instructions.

---

**Your bot is ready to go live! 🚀**
