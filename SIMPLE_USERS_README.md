# Simple Multi-User Setup for PSX Chainlit

## 🎯 What This Does

Adds 10 simple user accounts to your Chainlit application. All users have the same permissions - no role complexity.

## 🔑 User Accounts

```
user1  -> pass1
user2  -> pass2
user3  -> pass3
user4  -> pass4
user5  -> pass5
user6  -> pass6
user7  -> pass7
user8  -> pass8
user9  -> pass9
user10 -> pass10
```

## 🚀 Setup (2 steps)

### Step 1: Add users to database
```bash
psql -d your_database -f simple_users.sql
```

### Step 2: Start your app
Your Chainlit app will now accept these 10 users + your original admin login.

## 📝 Files Created

- `simple_users.sql` - SQL script to create users
- `simple_credentials.txt` - Login credentials  
- `simple_auth.py` - Simple authentication module
- Updated `Step8MCPClientPsxGPT.py` - Uses simple auth

## 🔄 How It Works

1. User enters `user1` / `pass1` (or any of the 10 accounts)
2. App checks database for username
3. Compares password (plain text, no hashing)
4. If match, user is logged in
5. Admin login still works as fallback

## ✅ That's It!

Simple, minimal, perfect for power user iteration. All users have identical permissions.