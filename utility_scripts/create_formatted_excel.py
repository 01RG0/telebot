"""
Create a properly formatted Excel file for bulk messaging
Based on your test users (9000000000 to 9000000099)
"""
import pandas as pd
from datetime import datetime

# Create sample data with your test users
data = {
    'target': [
        # Using actual test user IDs
        9000000000,
        9000000001,
        9000000002,
        9000000003,
        9000000004,
        9000000005,
        9000000006,
        9000000007,
        9000000008,
        9000000009,
        9000000010,
        9000000011,
        9000000012,
        9000000013,
        9000000014,
        9000000015,
        9000000016,
        9000000017,
        9000000018,
        9000000019,
        # You can also use names instead of IDs
        'محمد',
        'Ahmed',
        'علي',
        'Aisha',
        'Sarah'
    ],
    'message': [
        # Arabic messages
        'مرحبا! هذه رسالة تجريبية رقم 1 🎉',
        'شكرا لك على استخدام البوت 💙',
        'تحديث مهم: تم إضافة ميزات جديدة! ✨',
        'عزيزي المستخدم، نتمنى لك يوماً سعيداً ☀️',
        'مبروك! لقد ربحت جائزة خاصة 🎁',
        # English messages
        'Hello! This is test message #6 🚀',
        'Thank you for using our bot! 🙏',
        'Important update: New features added! 🎊',
        'Dear user, have a wonderful day! 🌟',
        'Congratulations! You won a special prize! 🏆',
        # Mixed messages
        'مرحبا Hello! Welcome to our bot 👋',
        'شكراً Thank you for your support! 💪',
        'تحديث Update: Check out new features! 🔥',
        'عرض خاص Special offer just for you! 🎯',
        'نشكرك We appreciate you! ❤️',
        # More Arabic
        'تذكير: لديك رسالة جديدة في النظام 📬',
        'لا تفوت فرصة العرض المحدود! ⏰',
        'شكراً لكونك جزءاً من مجتمعنا 🤝',
        'نحن هنا لخدمتك دائماً 💼',
        'استمتع بخدماتنا المميزة! ⭐',
        # Messages for name-based targeting
        'رسالة خاصة لمحمد! مرحباً بك 🎈',
        'Hello Ahmed! Special message for you 🎪',
        'مرحبا علي! كيف حالك اليوم؟ 😊',
        'Hi Aisha! Hope you\'re doing great! 🌺',
        'Hello Sarah! Thanks for being awesome! 🌸'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel with proper formatting
filename = 'test_send_formatted.xlsx'
df.to_excel(filename, index=False, engine='openpyxl')

print("=" * 70)
print("✅ PROPERLY FORMATTED EXCEL FILE CREATED")
print("=" * 70)
print(f"Filename: {filename}")
print(f"Total rows: {len(df)}")
print("\nFile structure:")
print("  Column A (target): Chat ID or Name")
print("  Column B (message): Message to send")
print("\n📋 Preview of first 5 rows:")
print("-" * 70)
print(df.head().to_string(index=False))
print("-" * 70)
print("\n🎯 How to use:")
print("  1. Open the admin GUI: python main.py")
print("  2. Click 'Load Excel (A=target, B=message)'")
print("  3. Select this file: test_send_formatted.xlsx")
print("  4. Click 'Send Imported Rows'")
print("  5. Confirm to send!")
print("=" * 70)
