#!/usr/bin/env python3
"""
Check what's actually in the database
"""

from database import db

print('Database connection test:')
try:
    users = db.get_users_simple()
    print('✅ Connected to database')
    print(f'✅ Found {len(users)} users')

    if users:
        print('Sample users:')
        for i, user in enumerate(users[:3]):
            print(f'  {i+1}. {user[1]} (ID: {user[0]})')

    # Check system stats
    stats = db.get_system_stats()
    print('\nSystem stats:')
    print(f'  Total messages: {stats["total_messages"]}')
    print(f'  Sent: {stats["total_sent"]}')
    print(f'  Failed: {stats["total_failed"]}')

    # Check recent user activity
    users_full, _, _ = db.get_users()
    if users_full:
        print('\nRecent user activity:')
        # Sort by last activity (most recent first)
        sorted_users = sorted(users_full, key=lambda x: x[3] or x[2] or datetime.min, reverse=True)
        for i, user in enumerate(sorted_users[:3]):
            chat_id, name, joined_at, last_activity, msg_count, status, phone = user
            print(f'  {name} (ID: {chat_id}) - Joined: {joined_at}, Messages: {msg_count}')

except Exception as e:
    print(f'❌ Database error: {e}')
    import traceback
    traceback.print_exc()
