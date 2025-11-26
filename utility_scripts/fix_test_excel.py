"""
Fix the existing 'test send.xlsx' file to have the correct format
"""
import pandas as pd
import os

# Read the existing file
try:
    filename = os.path.join('..', 'data', 'test_send.xlsx')
    df_old = pd.read_excel(filename)
    print("📄 Original file content:")
    print(df_old)
    print("\n" + "=" * 70)
except Exception as e:
    print(f"Could not read original file: {e}")

# Create properly formatted version
data = {
    'target': [
        # First 20 test user IDs
        9000000000, 9000000001, 9000000002, 9000000003, 9000000004,
        9000000005, 9000000006, 9000000007, 9000000008, 9000000009,
        9000000010, 9000000011, 9000000012, 9000000013, 9000000014,
        9000000015, 9000000016, 9000000017, 9000000018, 9000000019
    ],
    'message': [
        'مرحبا! رسالة تجريبية 1 🎉',
        'Hello! Test message 2 🚀',
        'شكراً لك! Thank you! 💙',
        'تحديث جديد New update! ✨',
        'مبروك! Congratulations! 🎁',
        'عرض خاص Special offer! 🎯',
        'نشكرك We appreciate you! ❤️',
        'تذكير Reminder! 📬',
        'فرصة محدودة Limited time! ⏰',
        'مرحباً بك Welcome! 👋',
        'شكراً Thank you! 🙏',
        'تحديث Update! 🔥',
        'جائزة Prize! 🏆',
        'عرض Offer! 💰',
        'خدمة Service! 💼',
        'ميزة Feature! ⭐',
        'تطوير Development! 🚀',
        'نجاح Success! 🎊',
        'فوز Win! 🏅',
        'شكر Thanks! 💝'
    ]
}

# Create new DataFrame
df_new = pd.DataFrame(data)

# Save with correct format
filename = os.path.join('..', 'data', 'test_send.xlsx')
df_new.to_excel(filename, index=False, engine='openpyxl')

print("✅ FIXED 'test send.xlsx'")
print("=" * 70)
print(f"Filename: {filename}")
print(f"Total rows: {len(df_new)}")
print("\n✅ Correct format:")
print("  Column A: 'target' (chat_id or name)")
print("  Column B: 'message' (text to send)")
print("\n📋 Preview:")
print("-" * 70)
print(df_new.head(10).to_string(index=False))
print("-" * 70)
print("\n🎯 Ready to use in admin GUI!")
print("=" * 70)
