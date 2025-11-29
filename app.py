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
import uuid

# Import bot components
from config import TELEGRAM_TOKEN, LOG_FILE
from database import db
from bot_handler import bot, run_bot_forever, send_bulk_by_chatids, send_template_to_selected, send_personalized_from_rows, send_personalized_from_template, request_phone_number

# Import optimization modules
from task_queue import get_task_queue
from excel_processor import ExcelProcessor
from message_sender import send_personalized_from_template_optimized, send_bulk_optimized

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
    """API endpoint for user growth data from actual database"""
    from datetime import datetime, timedelta
    import json

    try:
        # Get user growth data for last 30 days from database
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        users = db.get_users_simple()
        
        # Count users by join date
        daily_counts = {}
        cumulative = 0
        
        for user in users:
            joined_at = user[2]  # joined_at field
            if joined_at:
                date_key = joined_at.strftime('%Y-%m-%d')
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        # Generate 30-day labels and data
        labels = []
        data = []
        
        for i in range(31):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            labels.append(date_str)
            
            # Count cumulative users up to this date
            cumulative += daily_counts.get(date_str, 0)
            data.append(cumulative)
        
        result = {
            'labels': labels,
            'data': data
        }
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching user growth data: {e}")
        return jsonify({'error': str(e)}), 500

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
    """API endpoint for real message statistics from task queue"""
    try:
        task_queue = get_task_queue()
        
        # Count task statistics
        total_tasks = len(task_queue.results)
        completed_tasks = sum(1 for t in task_queue.results.values() if t.status == 'completed')
        failed_tasks = sum(1 for t in task_queue.results.values() if t.status == 'failed')
        
        # Calculate sent/failed from completed tasks
        total_sent = 0
        total_failed = 0
        
        for task in task_queue.results.values():
            if task.status == 'completed' and isinstance(task.data, dict):
                total_sent += task.data.get('sent', 0)
                total_failed += task.data.get('failed', 0)
        
        # Get user count
        users = db.get_users_simple()
        user_count = len(users)
        
        data = {
            'total_messages': total_sent + total_failed,
            'successful_sends': total_sent,
            'failed_sends': total_failed,
            'total_users': user_count,
            'active_tasks': sum(1 for t in task_queue.results.values() if t.status == 'running'),
            'pending_tasks': sum(1 for t in task_queue.results.values() if t.status == 'pending'),
        }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching message stats: {e}")
        return jsonify({
            'total_messages': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'total_users': 0,
            'active_tasks': 0,
            'pending_tasks': 0,
            'error': str(e)
        }), 500

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
            target_type = request.form.get('target_type')
            
            if target_type == 'all':
                # Submit background task for bulk sending
                users = db.get_users_simple()
                chat_ids = [u[0] for u in users]
                
                task_id = str(uuid.uuid4())
                task_queue = get_task_queue()
                task_queue.submit_task(
                    task_id,
                    send_bulk_optimized,
                    args=(chat_ids, template),
                    kwargs={'delay': config.SEND_DELAY}
                )
                
                flash(f"Message send started in background (Task ID: {task_id[:8]}). Check status in dashboard.", 'info')
                return redirect(url_for('task_status', task_id=task_id))
            
        elif action == 'excel':
            file_path = request.form.get('file_path')
            target_column = request.form.get('target_column')
            custom_columns = request.form.getlist('custom_columns')
            template = request.form.get('template')
            
            if not file_path or not target_column or not template:
                flash("Missing required fields: file path, target column, or template", 'danger')
                return render_template('send.html')
            
            try:
                # Validate Excel file first (lightweight operation)
                preview_result = ExcelProcessor.get_excel_preview(file_path)
                if 'error' in preview_result:
                    flash(f"Error: {preview_result['error']}", 'danger')
                    return render_template('send.html')
                
                # Validate columns exist
                columns = preview_result['columns']
                if target_column not in columns:
                    flash(f"Target column '{target_column}' not found in file", 'danger')
                    return render_template('send.html')
                
                for col in custom_columns:
                    if col not in columns:
                        flash(f"Column '{col}' not found in file", 'danger')
                        return render_template('send.html')
                
                # Submit background task for Excel processing and sending
                task_id = str(uuid.uuid4())
                task_queue = get_task_queue()
                
                def process_and_send_excel():
                    """Background task for Excel processing and sending"""
                    try:
                        # Read and prepare rows
                        df = ExcelProcessor.read_excel_chunked(file_path)
                        rows = ExcelProcessor.prepare_personalized_rows(
                            df, target_column, custom_columns
                        )
                        
                        # Send with progress tracking
                        sent, failed = send_personalized_from_template_optimized(
                            template, rows, delay=config.SEND_DELAY
                        )
                        
                        return {
                            'sent': len(sent),
                            'failed': len(failed),
                            'failed_details': failed[:10]  # Keep first 10 failures for inspection
                        }
                    finally:
                        # Clean up temp file
                        try:
                            os.remove(file_path)
                        except:
                            pass
                
                task_queue.submit_task(task_id, process_and_send_excel)
                flash(f"Excel processing started in background (Task ID: {task_id[:8]}). Processing {preview_result.get('row_count', 'N/A')} rows.", 'info')
                return redirect(url_for('task_status', task_id=task_id))
                    
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
        
        # Use optimized Excel processor
        result = ExcelProcessor.get_excel_preview(temp_path)
        
        if 'error' in result:
            os.remove(temp_path)
            return jsonify({'error': result['error']}), 400
        
        result['file_path'] = temp_path
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error previewing Excel file: {e}")
        return jsonify({'error': f'Error reading file: {str(e)}'}), 400

@app.route('/task-status/<task_id>')
@login_required
def task_status(task_id):
    """Display status of a background task"""
    task_queue = get_task_queue()
    result = task_queue.get_status(task_id)
    
    return render_template('task_status.html', task=result)

@app.route('/api/task-status/<task_id>')
@login_required
def api_task_status(task_id):
    """API endpoint for task status"""
    task_queue = get_task_queue()
    result = task_queue.get_status(task_id)
    
    return jsonify(result.to_dict())

@app.route('/api/task-status')
@login_required
def api_recent_tasks():
    """API endpoint for recent tasks list"""
    task_queue = get_task_queue()
    
    # Get all tasks and sort by creation time (newest first)
    all_tasks = list(task_queue.results.values())
    all_tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    # Return last 10 tasks
    recent_tasks = [task.to_dict() for task in all_tasks[:10]]
    
    return jsonify(recent_tasks)

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
