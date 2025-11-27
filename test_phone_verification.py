"""
Test script for phone verification feature
Run this to test database phone number methods
"""
from database import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_phone_verification():
    """Test phone number verification methods"""
    
    print("=" * 60)
    print("PHONE VERIFICATION FEATURE TEST")
    print("=" * 60)
    
    # Test user ID (use a test ID that doesn't exist in production)
    test_chat_id = 999999999
    test_name = "Test User"
    test_phone = "+201234567890"
    
    print("\n1. Testing add_or_update_user...")
    try:
        db.add_or_update_user(test_chat_id, test_name, "test")
        print("   ✅ User created successfully")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n2. Testing has_phone_number (should be False)...")
    try:
        has_phone = db.has_phone_number(test_chat_id)
        if not has_phone:
            print("   ✅ Correctly returns False (no phone number)")
        else:
            print("   ❌ Should return False but returned True")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3. Testing save_phone_number...")
    try:
        db.save_phone_number(test_chat_id, test_phone)
        print(f"   ✅ Phone number saved: {test_phone}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n4. Testing has_phone_number (should be True)...")
    try:
        has_phone = db.has_phone_number(test_chat_id)
        if has_phone:
            print("   ✅ Correctly returns True (phone number exists)")
        else:
            print("   ❌ Should return True but returned False")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n5. Testing get_user_phone...")
    try:
        phone = db.get_user_phone(test_chat_id)
        if phone == test_phone:
            print(f"   ✅ Phone number retrieved: {phone}")
        else:
            print(f"   ❌ Expected {test_phone} but got {phone}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n6. Testing duplicate phone save (should update, not duplicate)...")
    try:
        new_phone = "+201111111111"
        db.save_phone_number(test_chat_id, new_phone)
        retrieved_phone = db.get_user_phone(test_chat_id)
        if retrieved_phone == new_phone:
            print(f"   ✅ Phone number updated to: {new_phone}")
        else:
            print(f"   ❌ Expected {new_phone} but got {retrieved_phone}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n7. Cleaning up test data...")
    try:
        db.delete_user(test_chat_id)
        print("   ✅ Test user deleted")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n8. Testing has_phone_number for non-existent user...")
    try:
        has_phone = db.has_phone_number(test_chat_id)
        if not has_phone:
            print("   ✅ Correctly returns False for deleted user")
        else:
            print("   ❌ Should return False for deleted user")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the bot: python main.py or python app.py")
    print("2. Send a message to your bot on Telegram")
    print("3. Bot should request your phone number")
    print("4. Click the button to share your contact")
    print("5. Bot should save your phone and send welcome message")
    print("\nCheck app.log for detailed logs")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_phone_verification()
    except Exception as e:
        logger.exception(f"Test failed with error: {e}")
        print(f"\n❌ FATAL ERROR: {e}")
        print("Make sure MongoDB is running and accessible!")
