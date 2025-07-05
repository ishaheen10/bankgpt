#!/usr/bin/env python3
"""
Script to add multiple users to the Chainlit database for PSX Financial Analysis
"""
import os
import uuid
import hashlib
import secrets
from datetime import datetime
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password with salt for secure storage"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Use PBKDF2 with SHA256 for password hashing
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations
    )
    
    return password_hash.hex(), salt

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def create_users():
    """Create 10 users in the database"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set!")
        return
    
    try:
        # Create database engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Connected to database")
        
        # Define 10 users with different roles
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
        
        print(f"\n🔐 Creating {len(users_data)} users...")
        created_users = []
        
        for user_data in users_data:
            # Generate secure password
            password = generate_secure_password()
            password_hash, salt = hash_password(password)
            
            # Create user metadata
            metadata = {
                "role": user_data["role"],
                "name": user_data["name"],
                "project": "PSX",
                "password_hash": password_hash,
                "salt": salt,
                "created_by": "admin_script",
                "permissions": {
                    "read": True,
                    "analyze": True,
                    "export": user_data["role"] in ["manager", "analyst", "risk_analyst"]
                }
            }
            
            # Insert user into database
            try:
                user_id = str(uuid.uuid4())
                now = datetime.now()
                
                # Use SQLAlchemy text for the insert
                stmt = text('''
                    INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt")
                    VALUES (:id, :identifier, :metadata, :created_at, :updated_at)
                ''')
                
                session.execute(stmt, {
                    'id': user_id,
                    'identifier': user_data["username"],
                    'metadata': json.dumps(metadata),
                    'created_at': now,
                    'updated_at': now
                })
                
                session.commit()
                
                created_users.append({
                    "username": user_data["username"],
                    "password": password,
                    "name": user_data["name"],
                    "role": user_data["role"]
                })
                
                print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
                
            except Exception as e:
                print(f"❌ Error creating user {user_data['username']}: {e}")
                session.rollback()
        
        session.close()
        
        # Print user credentials
        print(f"\n📋 CREATED USERS SUMMARY:")
        print("=" * 70)
        print(f"{'Username':<15} {'Password':<15} {'Role':<12} {'Name'}")
        print("-" * 70)
        
        for user in created_users:
            print(f"{user['username']:<15} {user['password']:<15} {user['role']:<12} {user['name']}")
        
        print("\n" + "=" * 70)
        print("⚠️  IMPORTANT: Save these credentials securely!")
        print("💡 Users can now log in to the Chainlit application")
        print("🔐 Passwords are securely hashed in the database")
        
        # Save to file for reference
        with open("user_credentials.txt", "w") as f:
            f.write("PSX Financial Analysis - User Credentials\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"{'Username':<15} {'Password':<15} {'Role':<12} {'Name'}\n")
            f.write("-" * 50 + "\n")
            for user in created_users:
                f.write(f"{user['username']:<15} {user['password']:<15} {user['role']:<12} {user['name']}\n")
            f.write("\n" + "=" * 50 + "\n")
            f.write("⚠️  IMPORTANT: Keep this file secure and delete when no longer needed!\n")
        
        print(f"💾 Credentials also saved to: user_credentials.txt")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    create_users()