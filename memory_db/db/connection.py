# db/connection.py
# MongoDB Atlas connection — reads credentials from .env

import os
import sys
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# Load .env from the project root (one level up from db/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_database():
    """
    Returns a connected MongoDB database object.
    Reads MONGO_URI and DB_NAME from environment variables.
    Raises SystemExit on connection failure so the caller doesn't silently continue.
    """
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "memory_db")

    if not mongo_uri:
        print("[ERROR] MONGO_URI not found in .env file.")
        sys.exit(1)

    if not db_name:
        print("[ERROR] DB_NAME not found in .env file.")
        sys.exit(1)

    try:
        # tlsCAFile=certifi.where() fixes SSL cert verification on macOS
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        # Force a real connection attempt to catch errors early
        client.admin.command("ping")
        print(f"[OK] Connected to MongoDB Atlas — database: '{db_name}'")
        return client[db_name]

    except ConnectionFailure as e:
        print(f"[ERROR] Could not connect to MongoDB Atlas: {e}")
        sys.exit(1)

    except ConfigurationError as e:
        print(f"[ERROR] Bad MongoDB URI or configuration: {e}")
        sys.exit(1)
