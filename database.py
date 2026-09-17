import sqlite3
import os
from config import DB_PATH, SCHEMA_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # If database doesn't exist, create tables and seed data
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        print("[DB] Initializing new SQLite database from schema.sql...")
        conn = get_db()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("[DB] Database initialized successfully.")
