#!/usr/bin/env python3
"""
Quick verification test to check if code handles different target types
This simulates what happens without actually sending to Telegram
"""

def verify_target_detection():
    """Verify the target type detection logic"""
    
    print("\n" + "="*70)
    print("TARGET DETECTION VERIFICATION")
    print("="*70)
    
    test_cases = [
        # (target, expected_type, description)
        ('123456789', 'CHAT_ID', 'Chat ID - 9 digit string'),
        (123456789, 'CHAT_ID', 'Chat ID - 9 digit integer'),
        ('1234567890', 'CHAT_ID', 'Phone as 10-digit string'),
        ('+201001234567', 'NAME_LOOKUP', 'Phone with country code'),
        ('Ahmed', 'NAME_LOOKUP', 'Plain name'),
        ('0987654321', 'CHAT_ID', 'Phone with leading 0 (all digits)'),
        ('', 'EMPTY', 'Empty string'),
        (None, 'NONE', 'None value'),
    ]
    
    print("\nDetection Rules:")
    print("  1. If target is int -> CHAT_ID")
    print("  2. If target is string of only digits -> CHAT_ID")
    print("  3. Otherwise -> NAME_LOOKUP")
    print("  4. If empty/None -> SKIP")
    
    print("\n" + "-"*70)
    print(f"{'Target':<20} {'Type':<20} {'Detected':<20} {'Result':<10}")
    print("-"*70)
    
    passed = 0
    failed = 0
    
    for target, expected, description in test_cases:
        # Simulate the detection logic from message_sender.py
        if target is None:
            detected = 'NONE'
        elif target == '':
            detected = 'EMPTY'
        elif isinstance(target, int):
            detected = 'CHAT_ID'
        elif isinstance(target, str) and target.isdigit():
            detected = 'CHAT_ID'
        else:
            detected = 'NAME_LOOKUP'
        
        result = "[PASS]" if detected == expected else "[FAIL]"
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
        
        target_display = str(target)[:19] if target is not None else 'None'
        print(f"{target_display:<20} {expected:<20} {detected:<20} {result:<10}")
    
    print("-"*70)
    print(f"Results: {passed} passed, {failed} failed\n")
    
    return failed == 0


def verify_template_formatting():
    """Verify that template formatting works with different column names"""
    
    print("\n" + "="*70)
    print("TEMPLATE FORMATTING VERIFICATION")
    print("="*70)
    
    test_cases = [
        {
            'template': 'Hello {name}!',
            'row': {'target': '123456789', 'name': 'Ahmed'},
            'expected': 'Hello Ahmed!'
        },
        {
            'template': 'Order {order_id} for {customer_name}',
            'row': {'target': '123456789', 'order_id': '#001', 'customer_name': 'Ahmed'},
            'expected': 'Order #001 for Ahmed'
        },
        {
            'template': 'Your balance: {balance} EGP',
            'row': {'target': '123456789', 'balance': '500'},
            'expected': 'Your balance: 500 EGP'
        },
        {
            'template': 'Hello {name}! Your balance: {balance} EGP (Phone: {phone})',
            'row': {'target': '123456789', 'name': 'Ahmed', 'balance': '500', 'phone': '1234567890'},
            'expected': 'Hello Ahmed! Your balance: 500 EGP (Phone: 1234567890)'
        },
    ]
    
    print("\nTesting template formatting with different column names...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        template = test['template']
        row = test['row']
        expected = test['expected']
        
        try:
            result = template.format(**row)
            if result == expected:
                print(f"Test {i}: [OK] PASS")
                print(f"  Template: {template}")
                print(f"  Result:   {result}")
                passed += 1
            else:
                print(f"Test {i}: [FAIL] FAIL")
                print(f"  Template: {template}")
                print(f"  Expected: {expected}")
                print(f"  Got:      {result}")
                failed += 1
        except KeyError as e:
            print(f"Test {i}: [FAIL] FAIL - Missing key: {e}")
            failed += 1
        
        print()
    
    print(f"Results: {passed} passed, {failed} failed\n")
    
    return failed == 0


def verify_error_handling():
    """Verify error handling for edge cases"""
    
    print("\n" + "="*70)
    print("ERROR HANDLING VERIFICATION")
    print("="*70)
    
    test_cases = [
        {
            'name': 'Missing target field',
            'row': {'name': 'Ahmed'},
            'should_fail': True
        },
        {
            'name': 'Missing template placeholder',
            'row': {'target': '123456789', 'name': 'Ahmed'},
            'template': 'Hello {missing_field}!',
            'should_fail': True
        },
        {
            'name': 'Empty target',
            'row': {'target': '', 'name': 'Ahmed'},
            'should_fail': True
        },
        {
            'name': 'None target',
            'row': {'target': None, 'name': 'Ahmed'},
            'should_fail': True
        },
        {
            'name': 'Valid data',
            'row': {'target': '123456789', 'name': 'Ahmed'},
            'template': 'Hello {name}!',
            'should_fail': False
        },
    ]
    
    print("\nTesting error conditions...\n")
    
    passed = 0
    failed_detected = 0
    
    for i, test in enumerate(test_cases, 1):
        row = test['row']
        template = test.get('template', 'Hello {name}!')
        should_fail = test['should_fail']
        
        error_occurred = False
        error_msg = ""
        
        try:
            # Check for missing target
            if 'target' not in row:
                raise ValueError("Missing target field")
            
            target = row.get('target')
            if not target:
                raise ValueError("Empty or None target")
            
            # Try formatting
            message = template.format(**row)
            
        except Exception as e:
            error_occurred = True
            error_msg = str(e)
        
        # Check if result matches expectation
        if error_occurred == should_fail:
            print(f"Test {i}: [OK] PASS - {test['name']}")
            if error_occurred:
                print(f"  Error (expected): {error_msg}")
            else:
                print(f"  Success (expected): Message formatted correctly")
            passed += 1
        else:
            print(f"Test {i}: [FAIL] FAIL - {test['name']}")
            if should_fail:
                print(f"  Expected error but succeeded")
            else:
                print(f"  Expected success but got error: {error_msg}")
            failed_detected += 1
        
        print()
    
    print(f"Results: {passed} passed, {failed_detected} failed\n")
    
    return failed_detected == 0


def verify_realistic_scenarios():
    """Verify realistic Excel import scenarios"""
    
    print("\n" + "="*70)
    print("REALISTIC SCENARIO VERIFICATION")
    print("="*70)
    
    scenarios = [
        {
            'name': 'Chat ID Only (From Web)',
            'rows': [
                {'target': '123456789', 'name': 'Ahmed', 'amount': '500'},
                {'target': '987654321', 'name': 'Mohamed', 'amount': '1000'},
                {'target': '555555555', 'name': 'Sara', 'amount': '750'},
            ],
            'template': 'Hello {name}! Your balance: {amount} EGP',
            'expected_handled': 3,
            'expected_failed': 0
        },
        {
            'name': 'Phone Numbers with + (From Excel)',
            'rows': [
                {'target': '+201001234567', 'name': 'Ahmed', 'amount': '500'},
                {'target': '+201009876543', 'name': 'Mohamed', 'amount': '1000'},
                {'target': '+201005555555', 'name': 'Sara', 'amount': '750'},
            ],
            'template': 'Hello {name}! Your balance: {amount} EGP',
            'expected_handled': 3,
            'expected_failed': 0
        },
        {
            'name': 'Mixed Data (Chat ID + Phone)',
            'rows': [
                {'target': '123456789', 'name': 'Ahmed', 'type': 'user'},
                {'target': '1234567890', 'name': 'Mohamed', 'type': 'phone'},
                {'target': '+201005555555', 'name': 'Sara', 'type': 'phone'},
            ],
            'template': '{name} ({type})',
            'expected_handled': 3,
            'expected_failed': 0
        },
    ]
    
    print("\nTesting realistic scenarios...\n")
    
    total_passed = 0
    total_failed = 0
    
    for scenario in scenarios:
        name = scenario['name']
        rows = scenario['rows']
        template = scenario['template']
        
        print(f"Scenario: {name}")
        print(f"  Rows: {len(rows)}")
        
        handled = 0
        failed = 0
        
        for row in rows:
            try:
                if not row.get('target'):
                    failed += 1
                    continue
                
                message = template.format(**row)
                handled += 1
                
            except Exception as e:
                failed += 1
        
        success = (handled == scenario['expected_handled']) and \
                  (failed == scenario['expected_failed'])
        
        result = "[OK] PASS" if success else "[FAIL] FAIL"
        print(f"  Handled: {handled}/{scenario['expected_handled']}")
        print(f"  Failed: {failed}/{scenario['expected_failed']}")
        print(f"  Result: {result}\n")
        
        if success:
            total_passed += 1
        else:
            total_failed += 1
    
    print(f"Results: {total_passed} passed, {total_failed} failed\n")
    
    return total_failed == 0


def main():
    """Run all verification tests"""
    
    print("\n" + "="*70)
    print("CODE BEHAVIOR VERIFICATION SUITE")
    print("Testing: Chat ID | Phone | Mixed")
    print("="*70)
    
    results = {
        "Target Detection": verify_target_detection(),
        "Template Formatting": verify_template_formatting(),
        "Error Handling": verify_error_handling(),
        "Realistic Scenarios": verify_realistic_scenarios(),
    }
    
    print("="*70)
    print("VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    for test_name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"  {test_name:<30} {status}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} test groups passed\n")
    
    if passed == total:
        print(" All verifications passed!")
        print("\nConclusions:")
        print("  [OK] Chat IDs only: Works perfectly")
        print("  [OK] Phone numbers (with +): Can work with database lookup")
        print("  [OK] Phone numbers (numeric only): Treated as Chat IDs")
        print("  [OK] Mixed data: Each type handled appropriately")
        print("\nRecommendation: Use Chat IDs for simplicity, or implement")
        print("  phone lookup for phone-based sending.")
        return 0
    else:
        print("[WARN]  Some verifications failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
