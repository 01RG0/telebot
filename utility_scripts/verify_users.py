"""
Quick script to verify and display test users in the database
"""
import sys
import os

# Add parent directory to path to allow importing from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_users")

def verify_test_users():
    """Display all users in the database with details"""
    
    print("\n" + "=" * 70)
    print("DATABASE USER VERIFICATION")
    print("=" * 70)
    
    # Get all users
    all_users_data = db.get_users()
    all_users = all_users_data[0]
    
    if not all_users:
        print("\n⚠️  No users found in database!")
        return
    
    # Separate real and test users
    real_users = [u for u in all_users if u[0] < 9000000000]
    test_users = [u for u in all_users if u[0] >= 9000000000]
    
    # Statistics
    print(f"\n📊 STATISTICS:")
    print(f"   Total Users: {len(all_users)}")
    print(f"   Real Users (from Telegram): {len(real_users)}")
    print(f"   Test Users (generated): {len(test_users)}")
    print("=" * 70)
    
    # Display real users
    if real_users:
        print(f"\n👥 REAL USERS ({len(real_users)}):")
        print("-" * 70)
        for user in real_users:
            chat_id = user[0]
            name = user[1]
            phone = user[6]
            print(f"   ✓ {name:<30} | ID: {chat_id} | Phone: {phone}")
    
    # Display test users
    if test_users:
        print(f"\n🧪 TEST USERS ({len(test_users)}):")
        print("-" * 70)
        for user in test_users:
            chat_id = user[0]
            name = user[1]
            print(f"   • {name:<30} | ID: {chat_id}")
    
    print("\n" + "=" * 70)
    print("✅ Verification Complete!")
    print("=" * 70)
    
    # Show ID range for test users
    if test_users:
        min_id = min(u[0] for u in test_users)
        max_id = max(u[0] for u in test_users)
        print(f"\n📍 Test User ID Range: {min_id} to {max_id}")
        print(f"   Total Test Users: {len(test_users)}")
    
    return all_users, real_users, test_users


if __name__ == "__main__":
    try:
        verify_test_users()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure MongoDB is connected and database.py is working.")
