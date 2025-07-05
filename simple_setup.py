#!/usr/bin/env python3
"""
Simple script to add 10 users to Chainlit database
Basic passwords, no role complexity - just for power user iteration
"""
import uuid
import json
from datetime import datetime

def create_simple_users():
    """Create 10 simple users with basic passwords"""
    
    # Simple user list with basic passwords
    users = [
        {"username": "user1", "password": "pass1"},
        {"username": "user2", "password": "pass2"},
        {"username": "user3", "password": "pass3"},
        {"username": "user4", "password": "pass4"},
        {"username": "user5", "password": "pass5"},
        {"username": "user6", "password": "pass6"},
        {"username": "user7", "password": "pass7"},
        {"username": "user8", "password": "pass8"},
        {"username": "user9", "password": "pass9"},
        {"username": "user10", "password": "pass10"},
    ]
    
    sql_statements = []
    
    print("🔐 Creating 10 simple users...")
    
    for user in users:
        # Simple metadata - just store the plain password for now
        metadata = {
            "name": f"User {user['username'][-1]}",
            "password": user["password"],  # Store plain password (not secure but simple)
            "project": "PSX"
        }
        
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        sql = f"""INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('{user_id}', '{user["username"]}', '{json.dumps(metadata)}', '{now}', '{now}');"""
        
        sql_statements.append(sql)
        print(f"✅ {user['username']} -> {user['password']}")
    
    # Write SQL script
    with open("simple_users.sql", "w") as f:
        f.write("-- Simple PSX Users Setup\n")
        f.write("-- Run: psql -d your_database -f simple_users.sql\n\n")
        f.write("BEGIN;\n\n")
        
        for sql in sql_statements:
            f.write(sql + "\n")
        
        f.write("\nCOMMIT;\n")
    
    # Write simple credentials file
    with open("simple_credentials.txt", "w") as f:
        f.write("PSX Users - Simple Login Credentials\n")
        f.write("=" * 40 + "\n\n")
        
        for user in users:
            f.write(f"Username: {user['username']:<8} Password: {user['password']}\n")
        
        f.write("\n" + "=" * 40 + "\n")
        f.write("💡 All users have the same permissions\n")
    
    print(f"\n📄 Files created:")
    print(f"   📝 simple_users.sql")
    print(f"   🔑 simple_credentials.txt")
    
    print(f"\n🔑 Login Credentials:")
    print("=" * 30)
    for user in users:
        print(f"{user['username']:<8} -> {user['password']}")
    
    print(f"\n🚀 Setup: psql -d your_database -f simple_users.sql")

if __name__ == "__main__":
    create_simple_users()