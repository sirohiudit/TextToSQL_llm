import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "user_data" / "auth.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create sessions table

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    db_type TEXT,
    db_config TEXT,

    conversation_history TEXT DEFAULT '[]',
                                
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Create query_logs table

cursor.execute("""
CREATE TABLE IF NOT EXISTS query_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,

    question TEXT,
    generated_sql TEXT,

    database_type TEXT,

    execution_time REAL,

    success INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id),

    FOREIGN KEY(session_id)
        REFERENCES sessions(id)
)
""")


conn.commit()
conn.close()
