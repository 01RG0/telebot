"""
Create a test Excel file specifically targeting real users and test users
"""
import pandas as pd
import os

# Your specific real IDs
REAL_IDS = [
    5525117664,
    6350456343
]

# Some test IDs from the generator
TEST_IDS = [
    9000000000,
    9000000001,
    9000000002
]

data = {
    'target': REAL_IDS + TEST_IDS,
    'message': [
        # Messages for Real Users (You should receive these on Telegram!)
        '🔔 This is a REAL test message! If you see this, the bot works! ✅',
        '🔔 Another real test message for the second ID! 🚀',
        
        # Messages for Test Users (Only visible in logs/GUI)
        'Test message for fake user 0',
        'Test message for fake user 1',
        'Test message for fake user 2'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
# Save to Excel
filename = os.path.join('..', 'data', 'real_test_send.xlsx')
df.to_excel(filename, index=False, engine='openpyxl')

print("=" * 70)
print(f"✅ Created {filename}")
print("=" * 70)
print(f"Total recipients: {len(df)}")
print("\nRecipients:")
for i, target in enumerate(data['target']):
    type_ = "REAL USER (Check Telegram!)" if target in REAL_IDS else "TEST USER (Check Logs)"
    print(f"  {i+1}. {target} - {type_}")

print("\n" + "=" * 70)
print("👉 HOW TO TEST:")
print("1. Run 'python main.py'")
print("2. Click 'Load Excel'")
print(f"3. Select '{os.path.basename(filename)}' from the data folder")
print("4. Click 'Send Imported Rows'")
print("5. Check your Telegram app for the real messages!")
print("=" * 70)
