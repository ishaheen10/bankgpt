"""
Enhanced authentication module for Chainlit PSX Financial Analysis
Supports database-based user authentication with secure password hashing
"""
import os
import hashlib
import json
import chainlit as cl
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Keep admin credentials as fallback
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash and salt"""
    try:
        # Recreate the hash with the provided password and stored salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Same iteration count as used for hashing
        )
        
        return password_hash.hex() == stored_hash
    except Exception:
        return False

def get_user_from_database(username: str) -> Optional[dict]:
    """Retrieve user from database by username"""
    if not DATABASE_URL:
        return None
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Query user from database
        stmt = text('''
            SELECT id, identifier, metadata, "createdAt", "updatedAt"
            FROM "User"
            WHERE identifier = :username
        ''')
        
        result = session.execute(stmt, {'username': username}).fetchone()
        session.close()
        
        if result:
            metadata = json.loads(result[2]) if isinstance(result[2], str) else result[2]
            return {
                'id': result[0],
                'identifier': result[1],
                'metadata': metadata,
                'created_at': result[3],
                'updated_at': result[4]
            }
        
        return None
        
    except Exception as e:
        print(f"Database error in get_user_from_database: {e}")
        return None

@cl.password_auth_callback
def enhanced_auth_callback(username: str, password: str) -> Optional[cl.User]:
    """Enhanced authentication callback that checks database and fallback admin"""
    
    # First, check if it's the admin user (fallback)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD and ADMIN_USERNAME and ADMIN_PASSWORD:
        return cl.User(
            identifier=username, 
            metadata={
                "role": "admin", 
                "name": "Admin User", 
                "project": "PSX",
                "auth_method": "env_admin"
            }
        )
    
    # Check database users
    user_data = get_user_from_database(username)
    if user_data:
        metadata = user_data['metadata']
        
        # Extract password hash and salt from metadata
        stored_hash = metadata.get('password_hash')
        salt = metadata.get('salt')
        
        if stored_hash and salt:
            # Verify password
            if verify_password(password, stored_hash, salt):
                # Create Chainlit user with enhanced metadata
                user_metadata = {
                    "role": metadata.get('role', 'user'),
                    "name": metadata.get('name', username),
                    "project": metadata.get('project', 'PSX'),
                    "permissions": metadata.get('permissions', {}),
                    "user_id": user_data['id'],
                    "auth_method": "database",
                    "created_at": str(user_data['created_at'])
                }
                
                return cl.User(identifier=username, metadata=user_metadata)
    
    # Authentication failed
    return None

def get_user_role(user: cl.User) -> str:
    """Get user role from user metadata"""
    if user and user.metadata:
        return user.metadata.get('role', 'user')
    return 'user'

def get_user_permissions(user: cl.User) -> dict:
    """Get user permissions from user metadata"""
    if user and user.metadata:
        return user.metadata.get('permissions', {})
    return {}

def has_permission(user: cl.User, permission: str) -> bool:
    """Check if user has specific permission"""
    permissions = get_user_permissions(user)
    return permissions.get(permission, False)

# For backwards compatibility, export the auth callback
auth_callback = enhanced_auth_callback