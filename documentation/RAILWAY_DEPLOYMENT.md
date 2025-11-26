# Railway Deployment Guide

## 🚂 Deploying to Railway

Your Telegram bot is now ready for Railway deployment! Railway will run the bot 24/7 in the cloud.

### Prerequisites

1. **GitHub Account** - To connect your repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **MongoDB Atlas** - Already configured ✅
4. **Telegram Bot Token** - Already have it ✅

### 📋 Deployment Steps

#### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Telegram bot ready for Railway"
   ```

2. **Create GitHub Repository**:
   - Go to [github.com/new](https://github.com/new)
   - Create a new repository (e.g., "telegram-bot")
   - Don't initialize with README (you already have files)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

#### Step 2: Deploy on Railway

1. **Go to Railway**:
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"

2. **Connect GitHub**:
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your repository

3. **Configure Environment Variables**:
   Railway will ask for environment variables. Add these:

   ```
   TELEGRAM_TOKEN=8334074221:AAE8pGbyawYLnZmDlQd4fRXoW0p0hvO7koY
   MONGODB_URI=mongodb+srv://root:root@cluster0.xzdok6x.mongodb.net/?appName=Cluster0
   DATABASE_NAME=telegram_bot
   SEND_DELAY=0.5
   LOG_LEVEL=INFO
   WELCOME_MESSAGE=اهلا بيك في نظام المتابعة لمستر شادي الشرقاوي شكرا على ثقتك بنتمنى نكون عند حسن ظنك
   ```

4. **Deploy**:
   - Railway will automatically detect `Procfile`
   - Click "Deploy"
   - Wait for deployment to complete

#### Step 3: Verify Deployment

1. **Check Logs**:
   - In Railway dashboard, click on your project
   - Go to "Deployments" tab
   - Click on the latest deployment
   - View logs to confirm bot started

2. **Test Bot**:
   - Open Telegram
   - Send `/start` to your bot
   - You should receive the welcome message

### 🔧 Railway Configuration Files

Your project now includes:

| File | Purpose |
|------|---------|
| `bot_only.py` | Headless bot entry point (no GUI) |
| `Procfile` | Tells Railway how to start the app |
| `runtime.txt` | Specifies Python version |
| `requirements-railway.txt` | Minimal dependencies (no GUI) |

### 📊 What Runs on Railway

**Railway will run:**
- ✅ `bot_only.py` - Bot without GUI
- ✅ Telegram bot polling
- ✅ MongoDB Atlas connection
- ✅ User registration and messaging

**Railway will NOT run:**
- ❌ GUI (CustomTkinter) - Not supported on servers
- ❌ Admin interface - Use local `main.py` for admin tasks

### 💡 Workflow

**For Bot (24/7 on Railway):**
- Users interact with bot on Telegram
- Bot stores data in MongoDB Atlas
- Bot runs continuously in the cloud

**For Admin (Local on your PC):**
- Run `python main.py` locally
- Use GUI to manage users
- Send bulk messages
- Export/import Excel files

### 🔄 Updating Your Bot

When you make changes:

```bash
git add .
git commit -m "Update bot"
git push
```

Railway will automatically redeploy!

### 🐛 Troubleshooting

#### Bot not responding
1. Check Railway logs for errors
2. Verify environment variables are set
3. Check MongoDB Atlas IP whitelist (should be 0.0.0.0/0)

#### Database connection failed
1. Verify `MONGODB_URI` in Railway environment variables
2. Check MongoDB Atlas:
   - Database user exists
   - Password is correct
   - Network access allows all IPs (0.0.0.0/0)

#### Deployment failed
1. Check Railway build logs
2. Verify `requirements-railway.txt` has correct packages
3. Check Python version in `runtime.txt`

### 📝 Environment Variables in Railway

To add/edit environment variables in Railway:

1. Go to your project
2. Click "Variables" tab
3. Add or edit variables
4. Railway will automatically redeploy

### 🔐 Security Notes

✅ **Good practices:**
- Environment variables are encrypted in Railway
- `.env` file is in `.gitignore` (not pushed to GitHub)
- MongoDB Atlas has authentication

⚠️ **Important:**
- Never commit `.env` to GitHub
- Use strong passwords for MongoDB
- Regenerate bot token if exposed

### 💰 Railway Pricing

- **Free Tier**: $5 credit per month
- **Your bot usage**: Very minimal (likely stays free)
- **Upgrade**: Only if you need more resources

### 🎯 Testing Locally Before Railway

Test the headless version locally:

```bash
python bot_only.py
```

This runs the bot without GUI (same as Railway will run it).

### 📱 Admin Access While Bot is on Railway

**Option 1: Local Admin GUI**
```bash
python main.py
```
- Connects to same MongoDB Atlas
- Manages users remotely
- Sends messages through GUI

**Option 2: Direct MongoDB Access**
- Use MongoDB Compass
- Connect with your MongoDB URI
- View/edit data directly

### 🚀 Quick Railway Deployment Checklist

- [ ] Git repository initialized
- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project deployed on Railway
- [ ] Environment variables configured
- [ ] MongoDB Atlas IP whitelist set to 0.0.0.0/0
- [ ] Bot tested on Telegram
- [ ] Logs checked in Railway dashboard

### 📞 Support

If deployment fails:
1. Check Railway logs
2. Verify all environment variables
3. Test `bot_only.py` locally first
4. Check MongoDB Atlas connection

---

**Your bot is ready for Railway! 🎉**

The bot will run 24/7 in the cloud, and you can use the local GUI (`main.py`) anytime to manage users and send messages.
