"""
Simple authentication for Chainlit PSX - just plain password checking
Minimal code, no security complexity, for power user iteration
"""
import os
import json
import chainlit as cl
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME") 
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def get_user_from_database(username: str) -> Optional[dict]:
    """Get user from database - simple version"""
    if not DATABASE_URL:
        return None
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        stmt = text('SELECT identifier, metadata FROM "User" WHERE identifier = :username')
        result = session.execute(stmt, {'username': username}).fetchone()
        session.close()
        
        if result:
            metadata = json.loads(result[1]) if isinstance(result[1], str) else result[1]
            return {'identifier': result[0], 'metadata': metadata}
        
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

@cl.password_auth_callback
def simple_auth_callback(username: str, password: str) -> Optional[cl.User]:
    """Simple authentication - check plain password in database"""
    
    # Check admin first (fallback)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD and ADMIN_USERNAME:
        return cl.User(identifier=username, metadata={"name": "Admin", "project": "PSX"})
    
    # Check database users
    user_data = get_user_from_database(username)
    if user_data:
        stored_password = user_data['metadata'].get('password')
        
        # Simple password check - just compare strings
        if stored_password == password:
            return cl.User(
                identifier=username, 
                metadata={
                    "name": user_data['metadata'].get('name', username),
                    "project": "PSX"
                }
            )
    
    return None