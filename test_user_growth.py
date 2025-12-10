#!/usr/bin/env python3
"""
Test user growth API endpoint
"""

from app import app
from database import db
import json
import os

app.config['TESTING'] = True
client = app.test_client()

# Login first
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
login_response = client.post('/', data={'password': ADMIN_PASSWORD}, follow_redirects=True)
print(f"Login status: {login_response.status_code}")

# Test user growth endpoint
print("\nTesting user growth API...")
response = client.get('/api/analytics/user_growth')
if response.status_code == 200:
    data = json.loads(response.data.decode('utf-8'))
    print('User growth data:')
    print(f'Labels count: {len(data.get("labels", []))}')
    print(f'Data count: {len(data.get("data", []))}')
    print(f'First few labels: {data.get("labels", [])[:3]}')
    print(f'First few data points: {data.get("data", [])[:3]}')
    print(f'Last data point: {data.get("data", [])[-1] if data.get("data") else "None"}')
else:
    print(f'Error: {response.status_code}')
    print(response.data.decode('utf-8')[:500])

# Check actual users in database
print('\nChecking database users...')
users, _, _ = db.get_users()
print(f'Total users in database: {len(users)}')

# Count users by join date
from datetime import datetime, timedelta
from collections import defaultdict

join_dates = defaultdict(int)
for user in users:
    joined_at = user[2]
    if joined_at and isinstance(joined_at, datetime):
        date_key = joined_at.strftime('%Y-%m-%d')
        join_dates[date_key] += 1

print(f'Users with valid join dates: {sum(join_dates.values())}')
print(f'Unique join dates: {len(join_dates)}')

if join_dates:
    print('Sample join dates:')
    sorted_dates = sorted(join_dates.items())
    for date, count in sorted_dates[:5]:
        print(f'  {date}: {count} users')
    if len(sorted_dates) > 5:
        print(f'  ... and {len(sorted_dates) - 5} more dates')
