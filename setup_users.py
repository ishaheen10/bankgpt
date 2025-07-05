#!/usr/bin/env python3
"""
Simple script to add 10 users to your PSX Chainlit database
This script uses basic database connection without additional dependencies
"""
import os
import uuid
import hashlib
import secrets
import json
from datetime import datetime

def hash_password(password: str) -> tuple[str, str]:
    """Hash password with salt for secure storage"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    )
    return password_hash.hex(), salt

def generate_password(length: int = 12) -> str:
    """Generate a secure password"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def create_sql_script():
    """Create SQL script to insert users"""
    
    # Define 10 users
    users_data = [
        {"username": "analyst1", "name": "Financial Analyst 1", "role": "analyst"},
        {"username": "analyst2", "name": "Financial Analyst 2", "role": "analyst"},
        {"username": "manager1", "name": "Portfolio Manager 1", "role": "manager"},
        {"username": "manager2", "name": "Portfolio Manager 2", "role": "manager"},
        {"username": "researcher1", "name": "Research Associate 1", "role": "researcher"},
        {"username": "researcher2", "name": "Research Associate 2", "role": "researcher"},
        {"username": "trader1", "name": "Trading Specialist 1", "role": "trader"},
        {"username": "trader2", "name": "Trading Specialist 2", "role": "trader"},
        {"username": "risk_analyst", "name": "Risk Analyst", "role": "risk_analyst"},
        {"username": "compliance", "name": "Compliance Officer", "role": "compliance"},
    ]
    
    sql_statements = []
    credentials = []
    
    print("🔐 Generating users and SQL script...")
    
    for user_data in users_data:
        # Generate secure password and hash
        password = generate_password()
        password_hash, salt = hash_password(password)
        
        # Create metadata
        metadata = {
            "role": user_data["role"],
            "name": user_data["name"],
            "project": "PSX",
            "password_hash": password_hash,
            "salt": salt,
            "created_by": "setup_script",
            "permissions": {
                "read": True,
                "analyze": True,
                "export": user_data["role"] in ["manager", "analyst", "risk_analyst"]
            }
        }
        
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create SQL insert statement
        sql = f"""INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('{user_id}', '{user_data["username"]}', '{json.dumps(metadata).replace("'", "''")}', '{now}', '{now}');"""
        
        sql_statements.append(sql)
        
        credentials.append({
            "username": user_data["username"],
            "password": password,
            "name": user_data["name"],
            "role": user_data["role"]
        })
        
        print(f"✅ Generated: {user_data['username']} ({user_data['role']})")
    
    # Write SQL script
    with open("insert_users.sql", "w") as f:
        f.write("-- PSX Chainlit Users Setup Script\n")
        f.write("-- Run this script against your PostgreSQL database\n\n")
        f.write("BEGIN;\n\n")
        
        for sql in sql_statements:
            f.write(sql + "\n")
        
        f.write("\nCOMMIT;\n")
    
    # Write credentials file
    with open("user_credentials.txt", "w") as f:
        f.write("PSX Financial Analysis - User Credentials\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"{'Username':<15} {'Password':<15} {'Role':<12} {'Name'}\n")
        f.write("-" * 70 + "\n")
        
        for user in credentials:
            f.write(f"{user['username']:<15} {user['password']:<15} {user['role']:<12} {user['name']}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("⚠️  IMPORTANT: Keep this file secure!\n")
        f.write("💡 Users can now log in to the Chainlit application\n")
    
    print(f"\n📄 Created files:")
    print(f"   📝 insert_users.sql - Run this against your database")
    print(f"   🔑 user_credentials.txt - User login credentials")
    
    print(f"\n🚀 To setup users:")
    print(f"   1. Run: psql -d your_database -f insert_users.sql")
    print(f"   2. Or copy/paste the SQL statements into your database tool")
    print(f"   3. Share credentials from user_credentials.txt with your team")
    
    print(f"\n📋 CREATED USERS SUMMARY:")
    print("=" * 70)
    print(f"{'Username':<15} {'Password':<15} {'Role':<12} {'Name'}")
    print("-" * 70)
    
    for user in credentials:
        print(f"{user['username']:<15} {user['password']:<15} {user['role']:<12} {user['name']}")
    
    print("\n" + "=" * 70)
    print("✅ Setup complete! Your users are ready to login.")

if __name__ == "__main__":
    create_sql_script()