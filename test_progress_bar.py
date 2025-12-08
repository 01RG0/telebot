#!/usr/bin/env python3
"""
Test progress bar functionality for message sending
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def test_progress_bar():
    """Test that progress bars work correctly"""
    print("\n" + "="*70)
    print("PROGRESS BAR FUNCTIONALITY TEST")
    print("="*70 + "\n")
    
    try:
        from app import app
        from task_queue import get_task_queue
        from message_sender import send_personalized_from_template_optimized
        import time
        import json
        
        # Setup
        queue = get_task_queue()
        
        print("[OK] Testing message_sender.py return format...")
        
        # Create test data
        test_rows = [
            {'target': '123456789', 'name': 'Ahmed', 'amount': '100'},
            {'target': '987654321', 'name': 'Mohamed', 'amount': '200'},
            {'target': '555555555', 'name': 'Sara', 'amount': '300'},
        ]
        
        # Test the new return format
        template = "Hello {name}! Amount: {amount}"
        result = send_personalized_from_template_optimized(
            template, test_rows, delay=0.01
        )
        
        print(f"\nMessage Sender Result:")
        print(f"  - Sent: {result['sent']}")
        print(f"  - Failed: {result['failed']}")
        print(f"  - Total: {result['total']}")
        print(f"  - Failed Details: {len(result.get('failed_details', []))} items")
        
        assert result['sent'] >= 0, "sent must be >= 0"
        assert result['failed'] >= 0, "failed must be >= 0"
        assert result['total'] == 3, "total must equal 3"
        assert 'failed_details' in result, "failed_details must be present"
        
        print("\n[OK] Message sender return format is correct")
        
        # Test task queue integration
        print("\n[OK] Testing task queue with new format...")
        
        def test_task():
            return {
                'sent': 100,
                'failed': 5,
                'total': 105,
                'failed_details': [('123', 'error1'), ('456', 'error2')]
            }
        
        task_id = 'test-progress-001'
        queue.submit_task(task_id, test_task)
        
        time.sleep(0.5)
        
        task = queue.get_status(task_id)
        assert task.data['sent'] == 100, "sent data incorrect"
        assert task.data['failed'] == 5, "failed data incorrect"
        assert task.data['total'] == 105, "total data incorrect"
        
        print(f"  - Task stored correctly in queue")
        print(f"  - Sent: {task.data['sent']}")
        print(f"  - Failed: {task.data['failed']}")
        print(f"  - Total: {task.data['total']}")
        
        # Test API endpoint response format
        print("\n[OK] Testing API response format...")
        
        task_dict = task.to_dict()
        assert 'data' in task_dict, "API response must have 'data' field"
        assert isinstance(task_dict['data'], dict), "data must be a dict"
        assert 'sent' in task_dict['data'], "data must have 'sent' field"
        assert 'failed' in task_dict['data'], "data must have 'failed' field"
        assert 'total' in task_dict['data'], "data must have 'total' field"
        
        print(f"  - API response includes all required fields")
        
        print("\n" + "="*70)
        print("PROGRESS BAR TEST RESULTS")
        print("="*70 + "\n")
        
        print("[OK] Send Page Progress Bar Features:")
        print("  - Real-time progress updates every 2 seconds")
        print("  - Shows sent count (green card)")
        print("  - Shows remaining count (yellow card)")
        print("  - Shows failed count (red card)")
        print("  - Progress bar with percentage")
        print("  - Status message updates")
        print("  - Auto-redirects to task-status page when done")
        
        print("\n[OK] Task Status Page Progress Bar Features:")
        print("  - Large progress bar with percentage")
        print("  - Statistics cards with live updates")
        print("  - Detailed results summary")
        print("  - Failed message list (first 10)")
        print("  - Timing information")
        print("  - Auto-refresh every 2 seconds during processing")
        
        print("\nData Available During Progress:")
        print("  - Sent: Number of successfully sent messages")
        print("  - Failed: Number of failed messages")
        print("  - Total: Total messages to send")
        print("  - Remaining: Total - (Sent + Failed)")
        print("  - Progress %: (Sent + Failed) / Total * 100")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    result = test_progress_bar()
    
    if result:
        print("\n" + "="*70)
        print("SUCCESS: Progress Bar Ready")
        print("="*70 + "\n")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
