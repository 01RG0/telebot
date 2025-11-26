# Testing Guide - Bulk Messaging

## 🧪 Complete Testing Workflow

This guide shows you how to test all bulk messaging features with fake users.

### 📋 Prerequisites

- ✅ Bot is running (locally or on Railway)
- ✅ MongoDB is connected
- ✅ Admin GUI is accessible (`python main.py`)

---

## Step 1: Generate Test Users

### Option A: Using the Script (Recommended)

```bash
python generate_test_users.py
```

**Interactive Menu:**
```
1. Add test users       ← Choose this
2. Clear test users
3. Show statistics
4. Exit
```

**How many users?**
- For quick test: `20-50 users`
- For stress test: `100-500 users`
- For full test: `1000+ users`

**Example:**
```
Enter your choice (1-4): 1
How many test users to add? (default: 100): 200
```

This will add 200 fake users with Arabic and English names.

### Option B: Using Python Code

```python
from generate_test_users import generate_test_users

# Add 100 test users
generate_test_users(100)
```

---

## Step 2: Verify Test Users

### Check in Admin GUI

1. Run `python main.py`
2. Click **"Refresh"** button
3. You should see all test users in the list
4. Test users have IDs starting with `9000000000`

### Check Statistics

```bash
python generate_test_users.py
# Choose option 3: Show statistics
```

You'll see:
```
Total users: 201
Real users: 1
Test users: 200
```

---

## Step 3: Test Template Messages

### Simple Template Test

1. **Open Admin GUI** (`python main.py`)
2. **Select users**:
   - Click "Select All" to select all users
   - Or manually check specific users
3. **Enter template**:
   ```
   مرحبا {name}! هذه رسالة تجريبية
   ```
4. **Click "Send to Selected"**
5. **Confirm** the dialog

### Template with Variables

Try these templates:

**Arabic:**
```
مرحبا {name}! 
معرف المحادثة الخاص بك: {chat_id}
شكراً لاستخدامك البوت 🎉
```

**English:**
```
Hello {name}!
Your chat ID is: {chat_id}
Thank you for using our bot! 🚀
```

**Mixed:**
```
Hi {name}! 👋
ID: {chat_id}
نشكرك على ثقتك بنا
```

---

## Step 4: Test Excel Import

### Create Sample Excel File

```bash
python create_test_excel.py
```

**Choose option 1** to create a sample file with test data.

This creates: `test_messages_YYYYMMDD_HHMMSS.xlsx`

### Load and Send

1. **Open Admin GUI**
2. **Click "Load Excel (A=target, B=message)"**
3. **Select** the generated Excel file
4. **Verify** import message (e.g., "Imported 20 rows")
5. **Click "Send Imported Rows"**
6. **Confirm** the dialog

### Excel File Format

| Column A (target) | Column B (message) |
|-------------------|-------------------|
| 9000000000 | مرحبا! رسالة تجريبية 1 |
| محمد | Hello Mohamed! Test message |
| Ahmed | مرحبا أحمد! كيف حالك؟ |
| 9000000001 | Special offer for you! 🎁 |

**Target can be:**
- Chat ID (number): `9000000000`
- User name (text): `محمد` or `Ahmed`

---

## Step 5: Test Search & Filter

### Search by Name

1. In the search box, type: `محمد`
2. Only users with "محمد" in their name appear
3. Clear search to see all users again

### Search by ID

1. Type: `9000000005`
2. Only that specific user appears

### Select Filtered Users

1. Search for specific users
2. Click "Select All" (selects only visible users)
3. Send message to filtered group

---

## Step 6: Test Export

### Export to CSV

1. Click **"Export users"**
2. Choose **CSV** format
3. Save the file
4. Open in Excel to verify

### Export to Excel

1. Click **"Export users"**
2. Choose **Excel** format
3. Save as `.xlsx`
4. Open to verify all users are there

---

## Step 7: Performance Testing

### Small Batch (20 users)

```python
# In generate_test_users.py
generate_test_users(20)
```

**Expected:**
- Fast generation (< 5 seconds)
- Quick messaging (< 15 seconds with 0.5s delay)

### Medium Batch (100 users)

```python
generate_test_users(100)
```

**Expected:**
- Generation: ~10-20 seconds
- Messaging: ~50-60 seconds

### Large Batch (500 users)

```python
generate_test_users(500)
```

**Expected:**
- Generation: ~1-2 minutes
- Messaging: ~4-5 minutes

### Stress Test (1000+ users)

```python
generate_test_users(1000)
```

**Expected:**
- Generation: ~2-3 minutes
- Messaging: ~8-10 minutes

---

## Step 8: Test Different Scenarios

### Scenario 1: Mixed Languages

**Template:**
```
Hello {name}! مرحباً
Your ID: {chat_id}
شكراً Thank you! 🎉
```

### Scenario 2: Emojis

**Template:**
```
🎉 مبروك {name}! 🎊
You're user #{chat_id}
Keep using our bot! 🚀✨
```

### Scenario 3: Long Messages

**Template:**
```
عزيزي {name}،

نود أن نشكرك على استخدامك لخدماتنا. معرفك هو {chat_id}.

نحن نعمل باستمرار على تحسين تجربتك معنا.

شكراً لثقتك! 🙏
```

### Scenario 4: Name-based Targeting (Excel)

Create Excel with names instead of IDs:

| target | message |
|--------|---------|
| محمد | رسالة خاصة لمحمد |
| Ahmed | Special message for Ahmed |
| علي | مرحبا علي! |

---

## Step 9: Monitor & Debug

### Check Logs

```bash
type app.log
```

Look for:
```
INFO - Sent to 9000000000
INFO - Template send done. Sent: 20 Failed: 0
```

### Check MongoDB

Users are stored in MongoDB Atlas. You can verify:
1. Go to MongoDB Atlas
2. Browse Collections
3. Check `telegram_bot` → `users`

### Check Send Statistics

After sending, the GUI shows:
```
Sent: 200 | Failed: 0
```

---

## Step 10: Cleanup

### Remove Test Users

```bash
python generate_test_users.py
# Choose option 2: Clear test users
# Confirm: yes
```

This removes all users with `chat_id >= 9000000000`

### Keep Real Users

The cleanup script only removes test users. Your real users (from actual Telegram) are safe!

---

## 🎯 Quick Test Checklist

- [ ] Generate 50 test users
- [ ] Refresh GUI and verify users appear
- [ ] Select all and send template message
- [ ] Test search functionality
- [ ] Create sample Excel file
- [ ] Import and send personalized messages
- [ ] Export users to CSV
- [ ] Export users to Excel
- [ ] Test with Arabic messages
- [ ] Test with English messages
- [ ] Test with emojis
- [ ] Check logs for errors
- [ ] Clear test users when done

---

## 📊 Expected Results

### Successful Test

✅ All test users appear in GUI  
✅ Messages sent without errors  
✅ Logs show "Sent: X | Failed: 0"  
✅ Search works correctly  
✅ Export creates valid files  
✅ Excel import works  

### Common Issues

❌ **"Failed to send"**
- Check if bot is running
- Verify TELEGRAM_TOKEN in .env
- Test users can't receive messages (they're fake)
- This is normal for test users!

❌ **"No users found"**
- Run `generate_test_users.py` first
- Click "Refresh" in GUI
- Check MongoDB connection

❌ **"Import failed"**
- Verify Excel format (A=target, B=message)
- Check file has .xlsx extension
- Ensure pandas and openpyxl installed

---

## 💡 Pro Tips

1. **Test with small batches first** (20-50 users)
2. **Use test users for testing** (don't spam real users!)
3. **Check logs** after each test
4. **Clean up test users** when done
5. **Keep SEND_DELAY at 0.5s** to avoid Telegram rate limits

---

## 🚀 Advanced Testing

### Test Concurrent Operations

1. Generate 100 users
2. Open GUI
3. Start sending to 50 users
4. While sending, try searching
5. Verify GUI remains responsive

### Test Error Handling

1. Stop MongoDB temporarily
2. Try to add users
3. Check error handling
4. Restart MongoDB
5. Verify recovery

### Test Large Messages

Send messages with:
- 500+ characters
- Multiple lines
- Special characters
- Emojis

---

## 📝 Notes

- **Test users are fake** - They won't actually receive messages on Telegram
- **Sending will show "success"** - But messages won't be delivered (no real chat exists)
- **This is perfect for testing** - You can test the system without spamming real users
- **Real users** - Only users who actually send `/start` to your bot can receive messages

---

**Happy Testing! 🎉**

Use these tools to thoroughly test your bulk messaging system before using it with real users.
