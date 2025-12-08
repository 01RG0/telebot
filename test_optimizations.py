#!/usr/bin/env python3
"""
Test script to verify the optimization modules work correctly
Run this to ensure all new modules are properly integrated
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_task_queue():
    """Test the task queue system"""
    print("Testing task_queue module...")
    try:
        from task_queue import TaskQueue, get_task_queue, update_task_progress
        
        # Test basic task queue
        queue = TaskQueue(num_workers=1)
        queue.start()
        
        def sample_task(x, y):
            time.sleep(0.1)
            return x + y
        
        task_id = queue.submit_task("test_1", sample_task, args=(5, 3))
        time.sleep(0.5)  # Wait for task to complete
        
        result = queue.get_status(task_id)
        assert result.status == "completed", f"Expected 'completed', got '{result.status}'"
        assert result.data == 8, f"Expected 8, got {result.data}"
        
        queue.stop()
        print("  ✅ TaskQueue works correctly")
        return True
    except Exception as e:
        print(f"  ❌ TaskQueue test failed: {e}")
        return False

def test_excel_processor():
    """Test the Excel processor"""
    print("Testing excel_processor module...")
    try:
        from excel_processor import ExcelProcessor
        import pandas as pd
        import tempfile
        import os
        
        # Create a temporary Excel file
        df = pd.DataFrame({
            'chat_id': [123, 456, 789],
            'name': ['Alice', 'Bob', 'Charlie'],
            'phone': ['1234567890', '0987654321', '1111111111']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
            df.to_excel(tmp_path, index=False)
        
        try:
            # Test preview
            preview = ExcelProcessor.get_excel_preview(tmp_path)
            assert 'columns' in preview, "Preview missing 'columns'"
            assert preview['columns'] == ['chat_id', 'name', 'phone'], "Columns mismatch"
            assert 'row_count' in preview, "Preview missing 'row_count'"
            assert preview['row_count'] == 3, f"Expected 3 rows, got {preview['row_count']}"
            
            # Test column validation
            valid, msg = ExcelProcessor.validate_columns(df, ['chat_id', 'name'])
            assert valid, f"Validation failed: {msg}"
            
            valid, msg = ExcelProcessor.validate_columns(df, ['chat_id', 'missing_col'])
            assert not valid, "Should detect missing column"
            
            # Test row preparation
            rows = ExcelProcessor.prepare_personalized_rows(
                df, 'chat_id', ['name', 'phone']
            )
            assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
            assert rows[0]['target'] == 123, "First target should be 123"
            assert rows[0]['name'] == 'Alice', "First name should be 'Alice'"
            
            print("  ✅ ExcelProcessor works correctly")
            return True
        finally:
            os.remove(tmp_path)
            
    except Exception as e:
        print(f"  ❌ ExcelProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    try:
        from task_queue import get_task_queue
        from excel_processor import ExcelProcessor
        from message_sender import (
            send_personalized_from_template_optimized,
            send_bulk_optimized,
            send_template_to_selected_optimized
        )
        print("  ✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False

def test_config():
    """Test that config has new settings"""
    print("Testing config settings...")
    try:
        import config
        
        required_settings = [
            'TASK_QUEUE_WORKERS',
            'TASK_QUEUE_ENABLED',
            'EXCEL_CHUNK_SIZE',
            'MIN_SEND_DELAY',
            'MAX_SEND_DELAY',
            'BATCH_SEND_ENABLED',
            'TIMEOUT_SECONDS',
            'REQUEST_TIMEOUT'
        ]
        
        for setting in required_settings:
            assert hasattr(config, setting), f"Missing config setting: {setting}"
        
        print("  ✅ All config settings present")
        return True
    except Exception as e:
        print(f"  ❌ Config test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("OPTIMIZATION VERIFICATION TEST SUITE")
    print("="*60 + "\n")
    
    results = {
        "Config": test_config(),
        "Imports": test_imports(),
        "ExcelProcessor": test_excel_processor(),
        "TaskQueue": test_task_queue(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All optimizations are properly integrated!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
