# 📊 Export Users with Phone Numbers

## ✅ Feature Overview

I have added a new feature to the Web Admin Dashboard that allows you to export a complete list of users, including their verified phone numbers, into an Excel file.

## 🛠 What Was Changed

### 1. **Database Layer (`database.py`)**
- Added `get_users_with_phones()` method.
- Fetches: `Chat ID`, `Name`, `Phone Number`, `Phone Verified At`, `Joined At`.
- Sorts users alphabetically by name.

### 2. **Backend API (`app.py`)**
- Added new route: `/export/phones`.
- Generates a formatted Excel file (`.xlsx`).
- Auto-adjusts column widths for better readability.
- Handles users who haven't shared their phone numbers yet (shows "Not Shared").

### 3. **Frontend (`users.html`)**
- Added a new **"Export with Phones"** button.
- Located in the User Management header, next to the standard Export button.
- Styled with a primary blue color and phone icon.

## 🚀 How to Use

1. **Login** to your Web Admin Dashboard.
2. Navigate to the **Users** page.
3. Look for the buttons at the top right.
4. Click **"📱 Export with Phones"**.
5. The Excel file will download automatically.

## 📄 Excel File Structure

The downloaded file will have the following columns:

| Column | Description |
|--------|-------------|
| **Chat ID** | The user's Telegram ID |
| **Phone Number** | Verified phone number |

*Note: Users who haven't shared their phone number are excluded from this file.*

## 🧪 Verification

A test script `test_export_phones.py` verified that:
- Database query works correctly.
- Data is formatted properly.
- Excel file is generated successfully.

---
**Status:** ✅ Ready to use
**Updated:** 2025-11-27
