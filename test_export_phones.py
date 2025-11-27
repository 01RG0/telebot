"""
Test script for Phone Number Export feature
"""
import pandas as pd
from database import db
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_export_logic():
    print("=" * 60)
    print("EXPORT PHONES FEATURE TEST")
    print("=" * 60)

    # 1. Test Database Method
    print("\n1. Testing get_users_with_phones()...")
    try:
        users = db.get_users_with_phones()
        print(f"   ✅ Retrieved {len(users)} users from database")
        if len(users) > 0:
            print(f"   Sample user data: {users[0]}")
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return

    # 2. Test DataFrame Creation
    print("\n2. Testing DataFrame creation...")
    try:
        data = []
        for chat_id, name, phone, phone_verified_at, joined_at in users:
            if phone:
                data.append({
                    'Chat ID': chat_id,
                    'Phone Number': phone
                })
        
        df = pd.DataFrame(data)
        print("   ✅ DataFrame created successfully")
        print(f"   Columns: {df.columns.tolist()}")
    except Exception as e:
        print(f"   ❌ DataFrame Error: {e}")
        return

    # 3. Test Excel Generation
    print("\n3. Testing Excel file generation...")
    try:
        filename = "test_export_phones.xlsx"
        df.to_excel(filename, index=False, sheet_name='Users with Phones')
        
        if os.path.exists(filename):
            print(f"   ✅ Excel file '{filename}' created successfully")
            file_size = os.path.getsize(filename)
            print(f"   File size: {file_size} bytes")
            
            # Clean up
            os.remove(filename)
            print("   ✅ Test file cleaned up")
        else:
            print("   ❌ File was not created")
            
    except Exception as e:
        print(f"   ❌ Excel Generation Error: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_export_logic()
