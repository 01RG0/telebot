#!/usr/bin/env python3
"""
Performance Tuning Reference for Telebot Excel Sending Optimization

Use this guide to adjust settings based on your specific needs and platform constraints.
"""

# ==============================================================================
# RAILWAY FREE TIER (Recommended Default)
# ==============================================================================
RAILWAY_FREE_TIER = {
    "TASK_QUEUE_WORKERS": 1,              # Use 1 worker to save memory
    "SEND_DELAY": 0.5,                    # 0.5s between messages = 2 msg/sec
    "EXCEL_CHUNK_SIZE": 100,              # Process 100 rows at a time
    "BATCH_SEND_ENABLED": False,          # Don't batch sends
    "TIMEOUT_SECONDS": 600,               # 10 minute timeout per task
    
    "CHARACTERISTICS": {
        "max_concurrent_tasks": 1,
        "max_messages_per_batch": 500,
        "estimated_time_per_100_messages": "50 seconds",
        "memory_usage": "20-30 MB",
        "suitable_for": "Small to medium batches (100-500 messages)"
    }
}

# ==============================================================================
# RAILWAY HOBBY TIER ($5/month)
# ==============================================================================
RAILWAY_HOBBY_TIER = {
    "TASK_QUEUE_WORKERS": 2,              # Use 2 workers for better throughput
    "SEND_DELAY": 0.3,                    # 0.3s between messages = 3.3 msg/sec
    "EXCEL_CHUNK_SIZE": 200,              # Process 200 rows at a time
    "BATCH_SEND_ENABLED": True,           # Enable batch sending
    "TIMEOUT_SECONDS": 1200,              # 20 minute timeout per task
    
    "CHARACTERISTICS": {
        "max_concurrent_tasks": 2,
        "max_messages_per_batch": 2000,
        "estimated_time_per_1000_messages": "5 minutes",
        "memory_usage": "40-60 MB",
        "suitable_for": "Medium batches (500-2000 messages)"
    }
}

# ==============================================================================
# LOCAL DEVELOPMENT (Powerful Machine)
# ==============================================================================
LOCAL_DEVELOPMENT = {
    "TASK_QUEUE_WORKERS": 4,              # Multiple workers for speed
    "SEND_DELAY": 0.1,                    # Fast sending = 10 msg/sec
    "EXCEL_CHUNK_SIZE": 500,              # Large chunks = faster processing
    "BATCH_SEND_ENABLED": True,           # Batch sending enabled
    "TIMEOUT_SECONDS": 3600,              # 1 hour timeout
    
    "CHARACTERISTICS": {
        "max_concurrent_tasks": 4,
        "max_messages_per_batch": 10000,
        "estimated_time_per_1000_messages": "100 seconds",
        "memory_usage": "100-200 MB",
        "suitable_for": "Large batches and testing (1000+ messages)"
    }
}

# ==============================================================================
# PERFORMANCE TUNING GUIDELINES
# ==============================================================================

TUNING_GUIDE = """
┌─────────────────────────────────────────────────────────────────┐
│ WHAT TO ADJUST BASED ON YOUR NEEDS                              │
└─────────────────────────────────────────────────────────────────┘

1. INCREASE SPEED (more messages per second):
   ├─ Decrease SEND_DELAY: 0.5 → 0.3 → 0.1
   ├─ Increase TASK_QUEUE_WORKERS: 1 → 2 → 4
   ├─ Increase EXCEL_CHUNK_SIZE: 100 → 500
   ├─ Enable BATCH_SEND_ENABLED: False → True
   └─ WARNING: Watch for Telegram API rate limits!

2. SAVE MEMORY (lower memory usage):
   ├─ Decrease TASK_QUEUE_WORKERS: 4 → 2 → 1
   ├─ Decrease EXCEL_CHUNK_SIZE: 500 → 100 → 50
   ├─ Disable BATCH_SEND_ENABLED: True → False
   └─ Better for: Railway free tier, limited resources

3. INCREASE TIMEOUT (handle very large batches):
   ├─ Increase TIMEOUT_SECONDS: 600 → 1200 → 3600
   └─ For: 5000+ messages at slower speeds

4. IMPROVE RELIABILITY (reduce failures):
   ├─ Increase SEND_DELAY: 0.1 → 0.5 → 1.0
   ├─ Decrease TASK_QUEUE_WORKERS: 4 → 2 → 1
   └─ Monitor: Check logs for rate limit errors

┌─────────────────────────────────────────────────────────────────┐
│ QUICK REFERENCE TABLE                                           │
└─────────────────────────────────────────────────────────────────┘

Use Case              | SEND_DELAY | WORKERS | CHUNK_SIZE | TIMEOUT
─────────────────────┼────────────┼─────────┼────────────┼─────────
Slow/Reliable        | 1.0        | 1       | 50         | 600s
Normal (Railway Free)| 0.5        | 1       | 100        | 600s
Fast (Hobby Tier)    | 0.3        | 2       | 200        | 1200s
Very Fast (Local)    | 0.1        | 4       | 500        | 3600s
Ultra Safe           | 2.0        | 1       | 25         | 600s
Max Throughput       | 0.05       | 4       | 1000       | 3600s

┌─────────────────────────────────────────────────────────────────┐
│ MONITORING YOUR SETTINGS                                        │
└─────────────────────────────────────────────────────────────────┘

Check if settings are TOO AGGRESSIVE:
  ✗ Telegram errors in logs (rate limit exceeded)
  ✗ Many failed messages in results
  ✗ Memory usage spikes above 200MB
  → Solution: Increase SEND_DELAY or reduce WORKERS

Check if settings are TOO CONSERVATIVE:
  ✗ Sending 1000 messages takes 20+ minutes
  ✗ CPU usage is very low (<10%)
  ✗ Tasks timeout before completion
  → Solution: Decrease SEND_DELAY or increase WORKERS

Goldilocks Zone (Just Right):
  ✓ Completion in reasonable time (5-10 min per 1000 msgs)
  ✓ Memory usage 30-80MB
  ✓ CPU usage 40-70%
  ✓ Almost zero failures
  ✓ No timeout errors
"""

# ==============================================================================
# COMMON SCENARIOS & RECOMMENDED SETTINGS
# ==============================================================================

SCENARIOS = {
    "Small Newsletter (100 users)": {
        "SEND_DELAY": 0.5,
        "TASK_QUEUE_WORKERS": 1,
        "EXPECTED_TIME": "50 seconds",
        "NOTES": "Safe for all platforms. No tuning needed."
    },
    
    "Medium Broadcast (500 users)": {
        "SEND_DELAY": 0.3,
        "TASK_QUEUE_WORKERS": 1,
        "EXPECTED_TIME": "2-3 minutes",
        "NOTES": "Standard Railway settings. Reliable."
    },
    
    "Large Campaign (1000 users)": {
        "SEND_DELAY": 0.2,
        "TASK_QUEUE_WORKERS": 2,
        "EXPECTED_TIME": "5-8 minutes",
        "NOTES": "Requires Railway Hobby+ tier. Monitor logs."
    },
    
    "Massive Blast (5000+ users)": {
        "SEND_DELAY": 0.1,
        "TASK_QUEUE_WORKERS": 4,
        "EXPECTED_TIME": "10-15 minutes",
        "NOTES": "Requires powerful server. Watch Telegram limits."
    },
    
    "High Reliability Needed": {
        "SEND_DELAY": 1.0,
        "TASK_QUEUE_WORKERS": 1,
        "EXPECTED_TIME": "Longer, but safer",
        "NOTES": "Minimize failures. Slower but more reliable."
    },
    
    "Real-Time Interactive Bot": {
        "SEND_DELAY": 0.05,
        "TASK_QUEUE_WORKERS": 1,
        "EXPECTED_TIME": "Instant responses",
        "NOTES": "Use only for immediate single-user sends. Risk of rate limiting."
    }
}

# ==============================================================================
# ENVIRONMENT VARIABLE CONFIGURATION EXAMPLES
# ==============================================================================

ENV_EXAMPLES = """
# ============ RAILWAY FREE TIER (.env) ============
TASK_QUEUE_WORKERS=1
SEND_DELAY=0.5
EXCEL_CHUNK_SIZE=100
BATCH_SEND_ENABLED=False
TIMEOUT_SECONDS=600
REQUEST_TIMEOUT=30

# ============ RAILWAY HOBBY TIER (.env) ============
TASK_QUEUE_WORKERS=2
SEND_DELAY=0.3
EXCEL_CHUNK_SIZE=200
BATCH_SEND_ENABLED=True
TIMEOUT_SECONDS=1200
REQUEST_TIMEOUT=30

# ============ LOCAL TESTING (.env) ============
TASK_QUEUE_WORKERS=4
SEND_DELAY=0.1
EXCEL_CHUNK_SIZE=500
BATCH_SEND_ENABLED=True
TIMEOUT_SECONDS=3600
REQUEST_TIMEOUT=60

# ============ PRODUCTION HIGH-VOLUME (.env) ============
TASK_QUEUE_WORKERS=4
SEND_DELAY=0.2
EXCEL_CHUNK_SIZE=500
BATCH_SEND_ENABLED=True
TIMEOUT_SECONDS=3600
REQUEST_TIMEOUT=60
"""

# ==============================================================================
# TROUBLESHOOTING PERFORMANCE ISSUES
# ==============================================================================

TROUBLESHOOTING = """
ISSUE: App is crashing
SOLUTION:
  1. Reduce TASK_QUEUE_WORKERS to 1
  2. Increase SEND_DELAY to 0.5
  3. Decrease EXCEL_CHUNK_SIZE to 50
  4. Monitor logs for memory errors

ISSUE: Sending is very slow (< 1 msg/sec)
SOLUTION:
  1. Decrease SEND_DELAY (0.5 → 0.2 → 0.1)
  2. Increase TASK_QUEUE_WORKERS (if available memory)
  3. Check network speed (may be Telegram API slow)

ISSUE: Many messages failing
SOLUTION:
  1. Increase SEND_DELAY (less aggressive)
  2. Reduce TASK_QUEUE_WORKERS (one at a time)
  3. Check logs for Telegram rate limit errors
  4. Validate Excel data format

ISSUE: Tasks never finish
SOLUTION:
  1. Check if timeout is too short
  2. Increase TIMEOUT_SECONDS
  3. Monitor memory usage (might be memory limit)
  4. Check for infinite loops in logs

ISSUE: High memory usage
SOLUTION:
  1. Reduce TASK_QUEUE_WORKERS
  2. Decrease EXCEL_CHUNK_SIZE
  3. Set BATCH_SEND_ENABLED to False
  4. Process smaller files

ISSUE: App feels sluggish
SOLUTION:
  1. Reduce TASK_QUEUE_WORKERS
  2. Increase SEND_DELAY slightly
  3. Process smaller batches
  4. Free up system memory
"""

if __name__ == "__main__":
    print(TUNING_GUIDE)
    print("\n" + "="*70 + "\n")
    
    print("RECOMMENDED CONFIGURATIONS:\n")
    for scenario, settings in SCENARIOS.items():
        print(f"  {scenario}:")
        for key, value in settings.items():
            print(f"    {key}: {value}")
        print()
    
    print("="*70 + "\n")
    print(ENV_EXAMPLES)
    print("\n" + "="*70 + "\n")
    print(TROUBLESHOOTING)
