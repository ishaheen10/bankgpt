import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")

# Get admin username and password from environment
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@cl.data_layer
def get_data_layer():
    """Configure Chainlit to use SQLAlchemy with PostgreSQL for PSX project."""
    return SQLAlchemyDataLayer(conninfo=database_url)

@cl.auth
def auth_callback(username: str, password: str) -> cl.User | None:
    """Authenticate users for PSX analysis."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return cl.User(identifier=username, metadata={"role": "admin", "name": "Asfi", "project": "PSX"})
    return None 