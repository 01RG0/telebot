# Web Admin Panel Deployment Guide

## 🚀 Overview
Your Telegram bot now includes a full web-based admin panel! This allows you to:
- Manage users from any browser
- Send bulk messages with Excel upload
- View live logs
- Control the bot remotely

## 📦 New Features
- **Web Dashboard**: Access at `https://your-app-name.up.railway.app`
- **Login Protection**: Secure admin access
- **Excel Upload**: Drag & drop bulk messaging
- **Live Logs**: View bot activity in real-time

## 🛠️ Deployment Steps

### 1. Update Railway Environment Variables
Go to your Railway project settings and add/update these variables:

```env
# Existing variables
TELEGRAM_TOKEN=...
MONGODB_URI=...

# NEW variables
ADMIN_PASSWORD=your_secure_password  # Password for web login
FLASK_SECRET_KEY=random_secret_string # For session security
```

### 2. Deploy Updates
1. Commit and push the changes to GitHub:
   ```bash
   git add .
   git commit -m "Add web admin panel"
   git push
   ```
2. Railway will automatically detect the new `Procfile` and deploy the web app.

### 3. Access Your Admin Panel
1. In Railway, go to "Settings" -> "Networking".
2. Click "Generate Domain" to get a public URL (e.g., `web-production.up.railway.app`).
3. Open that URL in your browser.
4. Login with your `ADMIN_PASSWORD`.

## 🧪 Local Testing
To run the web panel on your PC before deploying:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**:
   ```bash
   python app.py
   ```

3. **Open Browser**:
   Go to `http://localhost:5000`

4. **Login**:
   Default password is `admin123` (or set `ADMIN_PASSWORD` in `.env`).

## 📝 Notes
- The bot runs automatically in the background when the web app starts.
- **Do not run `main.py`** on Railway anymore. The `Procfile` now uses `app.py`.
- You can still run `main.py` locally if you prefer the old GUI, but `app.py` gives you the web interface.
