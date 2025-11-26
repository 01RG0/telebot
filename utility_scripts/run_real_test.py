"""
Script to run the real test immediately without opening the GUI
"""
import pandas as pd
import logging
import sys
import os

# Add parent directory to path to allow importing from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot_handler import send_personalized_from_rows

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("test_runner")

def run_test():
    print("=" * 60)
    print("🚀 STARTING REAL TEST SEND")
    print("=" * 60)
    
    # 1. Read the Excel file
    filename = os.path.join('..', 'data', 'real_test_send.xlsx')
    print(f"📂 Reading file: {filename}...")
    try:
        df = pd.read_excel(filename)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # 2. Convert to format expected by bot
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "target": row['target'],
            "message": row['message']
        })
    
    print(f"✅ Loaded {len(rows)} messages to send.")
    print("-" * 60)
    
    # 3. Send messages
    print("📨 Sending messages now...")
    sent, failed = send_personalized_from_rows(rows)
    
    print("-" * 60)
    print("📊 TEST RESULTS:")
    print(f"✅ Successfully Sent: {len(sent)}")
    print(f"❌ Failed: {len(failed)}")
    
    if sent:
        print("\nSent to IDs:")
        for cid in sent:
            print(f"  - {cid}")
            
    if failed:
        print("\nFailed IDs (and reasons):")
        for cid, reason in failed:
            print(f"  - {cid}: {reason}")
            
    print("=" * 60)

if __name__ == "__main__":
    run_test()
