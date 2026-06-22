from sqlalchemy import text
from backend.database.auth_db import engine

with engine.begin() as conn:

 conn.execute(text("""
     CREATE TABLE IF NOT EXISTS users (
         id SERIAL PRIMARY KEY ,
         email VARCHAR(255) UNIQUE NOT NULL,
         password_hash TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
  """))

 # Create sessions table

 conn.execute(text("""
     CREATE TABLE IF NOT EXISTS sessions (
          id SERIAL PRIMARY KEY ,
          user_id INTEGER REFERENCES users(id),
          db_type VARCHAR(50),
          db_config TEXT,
          conversation_history TEXT DEFAULT '[]',                        
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
   """))

 # Create query_logs table

 conn.execute(text("""
     CREATE TABLE IF NOT EXISTS query_history(
         id SERIAL PRIMARY KEY,
         user_id INTEGER REFERENCES users(id),
         session_id INTEGER REFERENCES sessions(id),
         question TEXT,
         generated_sql TEXT,
         database_type VARCHAR(50),
         execution_time FLOAT,
         success BOOLEAN,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
  """))
 
 conn.execute(text("""
     CREATE INDEX IF NOT EXISTS idx_sessions_user
     ON sessions(user_id);
   """))

 conn.execute(text("""
     CREATE INDEX IF NOT EXISTS idx_history_user
     ON query_history(user_id);
    """))

 conn.execute(text("""
     CREATE INDEX IF NOT EXISTS idx_history_session
     ON query_history(session_id);
    """))

