#!/usr/bin/env python3
"""
Test dashboard display values
"""

from app import app
from database import db
import os
import re

app.config['TESTING'] = True
client = app.test_client()

# Login
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
client.post('/', data={'password': ADMIN_PASSWORD}, follow_redirects=True)

# Get dashboard
response = client.get('/dashboard')
print('Dashboard response status:', response.status_code)

# Extract user_count from HTML
html = response.data.decode('utf-8')
match = re.search(r'id="userCount">(\d+)</h3>', html)
if match:
    print('User count displayed in dashboard:', match.group(1))
else:
    print('Could not find user count in HTML')
    # Show a snippet around where it should be
    if 'userCount' in html:
        idx = html.find('userCount')
        print('Found userCount at position:', idx)
        print('Snippet:', html[idx-50:idx+50])

# Check actual database count
users = db.get_users_simple()
print('Actual users in database:', len(users))
