"""
Create sample Excel file for testing personalized messages
This generates an Excel file with test data for bulk messaging
"""
import pandas as pd
from datetime import datetime
import os

def create_sample_excel():
    """Create a sample Excel file with test messages"""
    
    # Sample data for personalized messages
    data = {
        'target': [
            # Mix of chat IDs and names
            9000000000,
            9000000001,
            9000000002,
            'محمد',
            'Ahmed',
            'علي',
            9000000003,
            'فاطمة',
            'Sarah',
            9000000004,
            'حسن',
            'Khaled',
            9000000005,
            'عائشة',
            'Omar',
            9000000006,
            9000000007,
            'يوسف',
            'Noor',
            9000000008
        ],
        'message': [
            # Various test messages in Arabic and English
            'مرحبا! هذه رسالة تجريبية رقم 1',
            'Hello! This is test message #2',
            'شكرا لك على استخدام البوت 🎉',
            'تحديث مهم: تم إضافة ميزات جديدة!',
            'Important update: New features added!',
            'عزيزي المستخدم، نتمنى لك يوماً سعيداً ☀️',
            'Dear user, have a wonderful day! 🌟',
            'تذكير: لديك رسالة جديدة في النظام',
            'Reminder: You have a new message in the system',
            'مبروك! لقد ربحت جائزة خاصة 🎁',
            'Congratulations! You won a special prize! 🏆',
            'نشكرك على ثقتك بنا دائماً',
            'Thank you for your continued trust',
            'عرض خاص لك فقط! تحقق من التفاصيل',
            'Special offer just for you! Check details',
            'تم تحديث حسابك بنجاح ✅',
            'Your account has been updated successfully ✅',
            'لا تفوت فرصة العرض المحدود!',
            'Don\'t miss the limited time offer!',
            'شكراً لكونك جزءاً من مجتمعنا 💙'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join('..', 'data', f"test_messages_{timestamp}.xlsx")
    
    # Save to Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print("=" * 60)
    print("SAMPLE EXCEL FILE CREATED")
    print("=" * 60)
    print(f"Filename: {filename}")
    print(f"Total rows: {len(df)}")
    print("\nFile structure:")
    print("  Column A (target): Chat ID or Name")
    print("  Column B (message): Message to send")
    print("\nYou can now:")
    print("  1. Open this file in Excel")
    print("  2. Edit the messages")
    print("  3. Load it in the admin GUI")
    print("  4. Send personalized messages to test users")
    print("=" * 60)
    
    # Show preview
    print("\nPreview of first 5 rows:")
    print(df.head().to_string(index=False))
    
    return filename


def create_template_excel():
    """Create an empty template Excel file"""
    
    # Empty template with headers and examples
    data = {
        'target': [
            'EXAMPLE: 123456789 or UserName',
            '',
            '',
            '',
            ''
        ],
        'message': [
            'EXAMPLE: Your message here',
            '',
            '',
            '',
            ''
        ]
    }
    
    df = pd.DataFrame(data)
    filename = os.path.join('..', 'data', "message_template.xlsx")
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"\n✅ Created template file: {filename}")
    print("Fill in your own data and load it in the admin GUI")
    
    return filename


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EXCEL MESSAGE FILE GENERATOR")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Create sample file with test data")
    print("  2. Create empty template")
    print("  3. Create both")
    print("=" * 60)
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    try:
        if choice == "1":
            filename = create_sample_excel()
            print(f"\n✅ Sample file created: {filename}")
        
        elif choice == "2":
            filename = create_template_excel()
        
        elif choice == "3":
            print("\n📝 Creating sample file...")
            sample_file = create_sample_excel()
            print("\n📝 Creating template file...")
            template_file = create_template_excel()
            print(f"\n✅ Created both files!")
            print(f"   - Sample: {sample_file}")
            print(f"   - Template: {template_file}")
        
        else:
            print("❌ Invalid choice")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure pandas and openpyxl are installed:")
        print("  pip install pandas openpyxl")
