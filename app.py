"""
Flask Web Application for Telegram Bot Admin
"""
import os
import logging
import threading
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from functools import wraps
from io import BytesIO, StringIO

# Import bot components
from config import TELEGRAM_TOKEN, LOG_FILE
from database import db
from bot_handler import bot, run_bot_forever, send_bulk_by_chatids, send_template_to_selected, send_personalized_from_rows, send_personalized_from_template

# Configure Logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("flask_app")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key_change_this")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Default password

# Start Bot Thread
if not os.environ.get("WERKZEUG_RUN_MAIN"):  # Prevent double start in debug mode
    bot_thread = threading.Thread(target=run_bot_forever, daemon=True)
    bot_thread.start()

# Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    users = db.get_users()
    user_count = len(users)
    
    # Get bot info
    try:
        bot_info = bot.get_me()
        bot_name = bot_info.first_name
        bot_username = bot_info.username
    except:
        bot_name = "Unknown"
        bot_username = "Unknown"

    return render_template('dashboard.html', user_count=user_count, bot_name=bot_name, bot_username=bot_username)

@app.route('/users')
@login_required
def users():
    all_users = db.get_users()
    return render_template('users.html', users=all_users)

@app.route('/users/delete/<int:chat_id>')
@login_required
def delete_user(chat_id):
    db.delete_user(chat_id)
    flash(f'User {chat_id} deleted', 'success')
    return redirect(url_for('users'))

@app.route('/export')
@login_required
def export_users():
    users = db.get_users()
    df = pd.DataFrame(users, columns=['chat_id', 'name'])
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Users')
    writer.close()
    output.seek(0)
    
    return send_file(output, download_name="users_export.xlsx", as_attachment=True)

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'template':
            template = request.form.get('template')
            # In a real app, we'd select users from a list, but for simplicity let's send to ALL for now or handle selection differently
            # For this version, let's assume "Send to All" or allow pasting IDs.
            # To keep it simple and powerful: "Send to All" button
            
            target_type = request.form.get('target_type')
            if target_type == 'all':
                users = db.get_users()
                chat_ids = [u[0] for u in users]
                sent, failed = send_template_to_selected(chat_ids, template)
                flash(f"Sent: {len(sent)}, Failed: {len(failed)}", 'info')
            
        elif action == 'excel':
            file = request.files['file']
            template = request.form.get('template')
            if file and file.filename.endswith('.xlsx') and template:
                try:
                    df = pd.read_excel(file)
                    # Convert to list of dicts with all columns
                    rows = df.to_dict('records')

                    sent, failed = send_personalized_from_template(template, rows)
                    flash(f"Personalized Send - Sent: {len(sent)}, Failed: {len(failed)}", 'success')
                except Exception as e:
                    flash(f"Error processing file: {e}", 'danger')
            else:
                flash("Invalid file or missing template. Please upload .xlsx and provide message template", 'danger')
                
    return render_template('send.html')

@app.route('/logs')
@login_required
def view_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            last_logs = lines[-100:] # Last 100 lines
            last_logs.reverse() # Newest first
    except:
        last_logs = ["Log file not found."]
    return render_template('logs.html', logs=last_logs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
