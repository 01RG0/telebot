"""
Flask Web Application for Telegram Bot Admin
"""
import os
import logging
import threading
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
from io import BytesIO, StringIO
from datetime import datetime
import config
import tempfile

# Import bot components
from config import TELEGRAM_TOKEN, LOG_FILE
from database import db
from bot_handler import bot, run_bot_forever, send_bulk_by_chatids, send_template_to_selected, send_personalized_from_rows, send_personalized_from_template, request_phone_number

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
    users = db.get_users_simple()
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
    # Get query parameters
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    users, total_count, total_pages = db.get_users(
        search=search if search else None,
        status_filter=status_filter if status_filter else None,
        page=page,
        per_page=per_page
    )

    return render_template('users.html',
                         users=users,
                         search=search,
                         status_filter=status_filter,
                         page=page,
                         per_page=per_page,
                         total_count=total_count,
                         total_pages=total_pages,
                         max=max,
                         min=min)

@app.route('/users/delete/<int:chat_id>')
@login_required
def delete_user(chat_id):
    db.delete_user(chat_id)
    flash(f'User {chat_id} deleted', 'success')
    return redirect(url_for('users'))

@app.route('/users/bulk_delete', methods=['POST'])
@login_required
def bulk_delete():
    chat_ids = request.form.getlist('chat_ids')
    deleted_count = 0
    for chat_id in chat_ids:
        try:
            db.delete_user(int(chat_id))
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete user {chat_id}: {e}")

    flash(f'Successfully deleted {deleted_count} users', 'success')
    return redirect(url_for('users'))

@app.route('/users/<int:chat_id>')
@login_required
def user_detail(chat_id):
    user = db.get_user_by_chat(chat_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('users'))

    # For now, just show basic info. Later we can add activity history
    return render_template('user_detail.html', user=user)

@app.route('/api/analytics/user_growth')
@login_required
def api_user_growth():
    """API endpoint for user growth data"""
    from datetime import datetime, timedelta
    import json

    # Get user growth data for last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    # This is a simplified version - in production you'd aggregate from database
    # For now, return mock data
    data = {
        'labels': [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)],
        'data': [i * 2 for i in range(31)]  # Mock growth data
    }

    return json.dumps(data)

@app.route('/settings')
@login_required
def settings():
    import sys
    import flask
    return render_template('settings.html',
                         welcome_message=config.WELCOME_MESSAGE,
                         send_delay=config.SEND_DELAY,
                         log_level=config.LOG_LEVEL,
                         log_file=config.LOG_FILE,
                         python_version=sys.version.split()[0],
                         flask_version=flask.__version__,
                         start_time=datetime.utcnow().isoformat())

@app.route('/settings/bot', methods=['POST'])
@login_required
def update_bot_settings():
    # Update bot configuration (would need to persist to .env or database)
    welcome_message = request.form.get('welcome_message')
    send_delay = request.form.get('send_delay')
    log_level = request.form.get('log_level')

    # For now, just flash success (in production, save to config)
    flash('Bot settings updated successfully', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/admin', methods=['POST'])
@login_required
def update_admin_settings():
    admin_password = request.form.get('admin_password')
    # Update admin password logic would go here
    flash('Admin settings updated successfully', 'success')
    return redirect(url_for('settings'))

@app.route('/api/settings/export')
@login_required
def export_settings():
    import json
    settings_data = {
        'welcome_message': config.WELCOME_MESSAGE,
        'send_delay': config.SEND_DELAY,
        'log_level': config.LOG_LEVEL,
        'exported_at': datetime.utcnow().isoformat()
    }
    return json.dumps(settings_data)

@app.route('/export/analytics')
@login_required
def export_analytics():
    """Export analytics data as CSV"""
    import csv
    from io import StringIO

    # Get user data
    users = db.get_users_simple()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Chat ID', 'Name', 'Joined At', 'Last Activity', 'Message Count', 'Status'])

    for user in users:
        writer.writerow([
            user[0],  # chat_id
            user[1],  # name
            user[2].strftime('%Y-%m-%d %H:%M:%S') if user[2] else '',  # joined_at
            user[3].strftime('%Y-%m-%d %H:%M:%S') if user[3] else '',  # last_activity
            user[4],  # message_count
            user[5]   # status
        ])

    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'analytics_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/analytics/message_stats')
@login_required
def api_message_stats():
    """API endpoint for message statistics"""
    import json

    # Mock message statistics
    data = {
        'total_messages': 1250,
        'successful_sends': 1180,
        'failed_sends': 70,
        'average_response_time': 2.3
    }

    return json.dumps(data)

@app.route('/export')
@login_required
def export_users():
    users = db.get_users_simple()
    df = pd.DataFrame(users, columns=['chat_id', 'name'])
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Users')
    writer.close()
    output.seek(0)
    
    return send_file(output, download_name="users_export.xlsx", as_attachment=True)

@app.route('/export/phones')
@login_required
def export_users_with_phones():
    """Export users with phone numbers to Excel"""
    users = db.get_users_with_phones()
    
    # Prepare data for DataFrame
    data = []
    for chat_id, name, phone, phone_verified_at, joined_at in users:
        # Only include users with phone numbers
        if phone:
            data.append({
                'Chat ID': chat_id,
                'Phone Number': phone
            })
    
    df = pd.DataFrame(data)
    
    # Create Excel file
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Users with Phones')
    
    # Auto-adjust column widths
    worksheet = writer.sheets['Users with Phones']
    for idx, col in enumerate(df.columns):
        max_length = max(
            df[col].astype(str).apply(len).max(),
            len(col)
        ) + 2
        worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    writer.close()
    output.seek(0)
    
    filename = f"users_phones_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True)

@app.route('/users/request_missing_phones', methods=['POST'])
@login_required
def request_missing_phones():
    """Send phone number request to all users who haven't shared it"""
    try:
        # Get users without phones
        chat_ids = db.get_users_without_phone()
        
        if not chat_ids:
            flash('All users have already shared their phone numbers!', 'info')
            return redirect(url_for('users'))
            
        # Send requests
        count = 0
        for chat_id in chat_ids:
            try:
                request_phone_number(chat_id)
                count += 1
                # Add a small delay to avoid hitting rate limits if there are many users
                import time
                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Failed to request phone from {chat_id}: {e}")
                
        flash(f'Successfully sent phone number requests to {count} users.', 'success')
        
    except Exception as e:
        logger.error(f"Error in request_missing_phones: {e}")
        flash(f'An error occurred: {e}', 'danger')
        
    return redirect(url_for('users'))

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
                users = db.get_users_simple()
                chat_ids = [u[0] for u in users]
                sent, failed = send_template_to_selected(chat_ids, template)
                flash(f"Sent: {len(sent)}, Failed: {len(failed)}", 'info')
            
        elif action == 'excel':
            file_path = request.form.get('file_path')
            target_column = request.form.get('target_column')
            custom_columns = request.form.getlist('custom_columns')
            template = request.form.get('template')
            
            if not file_path or not target_column or not template:
                flash("Missing required fields: file path, target column, or template", 'danger')
                return render_template('send.html')
            
            try:
                # Read the Excel file
                df = pd.read_excel(file_path)
                
                # Validate columns exist
                if target_column not in df.columns:
                    flash(f"Target column '{target_column}' not found in file", 'danger')
                    return render_template('send.html')
                
                for col in custom_columns:
                    if col not in df.columns:
                        flash(f"Column '{col}' not found in file", 'danger')
                        return render_template('send.html')
                
                # Prepare rows with renamed target column
                rows = []
                for idx, row in df.iterrows():
                    row_dict = row.to_dict()
                    # Create new dict with 'target' key pointing to target_column value
                    prepared_row = {
                        'target': row_dict.get(target_column),
                    }
                    # Add selected custom columns
                    for col in custom_columns:
                        prepared_row[col] = row_dict.get(col)
                    rows.append(prepared_row)
                
                # Send personalized messages
                sent, failed = send_personalized_from_template(template, rows)
                flash(f"Personalized Send - Sent: {len(sent)}, Failed: {len(failed)}", 'success')
                
                # Clean up temp file
                try:
                    os.remove(file_path)
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Error processing Excel file: {e}")
                flash(f"Error processing file: {e}", 'danger')
                
    return render_template('send.html')

@app.route('/preview-excel', methods=['POST'])
@login_required
def preview_excel():
    """Preview Excel file and return column names and sample data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file or not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'Please upload an .xlsx file'}), 400
        
        # Save to temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(temp_fd)
        file.save(temp_path)
        
        # Read Excel file
        df = pd.read_excel(temp_path)
        
        if df.empty:
            os.remove(temp_path)
            return jsonify({'error': 'Excel file is empty'}), 400
        
        columns = list(df.columns)
        sample_data = df.iloc[0].to_dict()
        
        # Convert sample data to serializable format
        sample_data_serialized = {}
        for key, value in sample_data.items():
            if pd.isna(value):
                sample_data_serialized[key] = '[empty]'
            else:
                sample_data_serialized[key] = str(value)
        
        return jsonify({
            'columns': columns,
            'sample_data': sample_data_serialized,
            'file_path': temp_path
        })
    
    except Exception as e:
        logger.error(f"Error previewing Excel file: {e}")
        return jsonify({'error': f'Error reading file: {str(e)}'}), 400

@app.route('/logs')
@login_required
def view_logs():
    # Get filter parameters
    log_level = request.args.get('level', '').upper()
    search_term = request.args.get('search', '').strip()
    date_filter = request.args.get('date', '')

    try:
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()

        # Filter logs
        filtered_logs = []
        for line in all_lines:
            # Level filter
            if log_level and f'- {log_level} -' not in line:
                continue

            # Search filter
            if search_term and search_term.lower() not in line.lower():
                continue

            # Date filter (basic YYYY-MM-DD check)
            if date_filter and not line.startswith(date_filter):
                continue

            filtered_logs.append(line.strip())

        # Get last 100 filtered logs
        last_logs = filtered_logs[-100:]
        last_logs.reverse()  # Newest first

    except:
        last_logs = ["Log file not found."]

    return render_template('logs.html',
                         logs=last_logs,
                         log_level=log_level,
                         search_term=search_term,
                         date_filter=date_filter)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
