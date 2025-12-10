#!/usr/bin/env python3
"""
Check if Flask app is using the same database
"""

import os
print('Environment check:')
print(f'Current directory: {os.getcwd()}')
print(f'MongoDB URI: {os.getenv("MONGODB_URI", "mongodb://localhost:27017/")}')
print(f'Database name: {os.getenv("DATABASE_NAME", "telegram_bot")}')

# Test database connection in app context
from app import app
with app.app_context():
    from database import db
    users = db.get_users_simple()
    print(f'\nIn Flask app context:')
    print(f'Users count: {len(users)}')

    # Test the dashboard endpoint
    from flask import url_for
    with app.test_client() as client:
        # Login first
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
        login_response = client.post('/', data={'password': ADMIN_PASSWORD}, follow_redirects=True)

        # Get dashboard
        dashboard_response = client.get('/dashboard')
        print(f'Dashboard response: {dashboard_response.status_code}')

        # Extract user count from HTML
        import re
        html = dashboard_response.data.decode('utf-8')
        match = re.search(r'id="userCount">(\d+)</h3>', html)
        if match:
            print(f'User count in dashboard: {match.group(1)}')
        else:
            print('Could not extract user count from dashboard HTML')
