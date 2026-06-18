from fastapi import (
    FastAPI,
    Depends,
)

from pydantic import BaseModel
from fastapi import UploadFile, File
import shutil
import time
from pathlib import Path
import sqlite3

from backend.app.cache.schema_cache import SchemaCache
from backend.app.security.authentication.auth import (
    hash_password,
    verify_password,
    create_access_token
)

from backend.app.security.authentication.models import (
    TokenResponse,
    UserCreate,
    UserLogin
)
from backend.app.security.authentication.dependencies import (
    get_current_user
)
from backend.app.security.authentication.query_history_manager import QueryHistoryManager
from backend.app.security.authentication.session_manager import SessionManager
from backend.database.database_manager import DatabaseManager
from backend.app.text_to_sql_pipeline import TextToSQLPipeline
from backend.app.cache.redis_client import redis_client

app = FastAPI(
    title="Text-to-SQL AI API"
)
try:

    redis_client.ping()

    print(
        "Redis connected successfully"
    )

except Exception as e:

    print(
        f"Redis unavailable: {e}"
    )

# =====================================
# LOAD PIPELINE
# =====================================

pipeline = TextToSQLPipeline()
DB_PATH = r"C:\projects\Text_to_SQL_llm\backend\database\user_data\auth.db"
# =====================================
# REQUEST MODEL
# =====================================

class QueryRequest(BaseModel):

    session_id: int
    question: str
    
 # =====================================
 # ROOT ENDPOINT
 # =====================================
def build_engine_from_session(session):

    db_manager = DatabaseManager()

    db_type = session["db_type"]

    config = session["db_config"]

    if db_type == "sqlite":

        db_manager.connect_sqlite(
            config["path"]
        )

    elif db_type == "csv":

        db_manager.connect_csv(
            config["path"]
        )

    elif db_type == "postgresql":

        db_manager.connect_postgresql(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            username=config["username"],
            password=config["password"]
        )

    elif db_type == "mysql":

        db_manager.connect_mysql(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            username=config["username"],
            password=config["password"]
        )

    return db_manager.get_engine()

@app.get("/")
def root():

    return {
        "message": "Text-to-SQL API is running!"
    }

#====================================
# SINGUP ENDPOINT
#====================================

@app.post("/signup")
def signup(user: UserCreate):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id FROM users WHERE email=?",
        (user.email,)
    ).fetchone()

    if existing:
        return {"error": "Email already exists"}

    hashed = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users(email,password_hash)
        VALUES (?,?)
        """,
        (user.email, hashed)
    )

    conn.commit()

    user_id = cursor.lastrowid

    if user_id is None:
        conn.close()
        return {"error": "Failed to create user."}

    conn.close()

    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token
    )

#====================================
# LOGIN ENDPOINT
#=====================================

@app.post("/login")
def login(user: UserLogin):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    row = cursor.execute(
        """
        SELECT id,password_hash
        FROM users
        WHERE email=?
        """,
        (user.email,)
    ).fetchone()

    conn.close()

    if not row:
        return {"error": "Invalid credentials"}

    user_id = row[0]
    password_hash = row[1]

    if not verify_password(
        user.password,
        password_hash
    ):
        return {"error": "Invalid credentials"}

    token = create_access_token(user_id)

    return TokenResponse(
        access_token=token
    )

# =====================================
# ASK ENDPOINT
# =====================================

@app.post("/ask")
def ask_question(request: QueryRequest, user_id: int = Depends(get_current_user)):
    
     session = SessionManager.get_session(
          request.session_id,
          user_id
        )
     if session is None:

          return {
              "success": False,
              "error": "Session not found."
            }
     engine = build_engine_from_session(session)
     start_time = time.time()

     response = pipeline.run(
            question=request.question,
            engine=engine,
            database_type=session["db_type"],
            conversation_history=session["conversation_history"]
     )
     elapsed_time = time.time() - start_time
     print("Updated history")
     print(response.get("conversation_history", []))

     SessionManager.update_history(
          request.session_id,
          response.get(
             "conversation_history",
              []
            ) 
        )
     QueryHistoryManager.save_query(
          user_id=user_id,
          session_id=request.session_id,
          question=request.question,
          generated_sql=response.get(
               "generated_sql",
              ""
           ),
          database_type=response.get(
               "database_type",
               ""
            ),
         execution_time=elapsed_time,
         success=response.get(
              "execution_result",
              {}
            ).get(
               "success",
               False
            )
        )
     return response

@app.get("/history")
def get_history(
    user_id: int = Depends(
        get_current_user
    )
):

    return QueryHistoryManager.get_user_history(
        user_id
    )

@app.post("/upload-sqlite")
def upload_sqlite_db(file: UploadFile = File(...), user_id: int = Depends(get_current_user)):

    uploads_dir = Path("uploads")

    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / file.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )
    
    session_id = SessionManager.create_session(
       user_id=user_id,
       db_type="sqlite",
       db_config={
        "path": str(file_path)
        }
    )
    schema_key = SchemaCache.create_key(
       "sqlite",
       str(file_path)
   )

    SchemaCache.invalidate(
      schema_key
    )

    
    return {
        "success": True,
        "session_id": session_id,
        "message": f"SQLite database uploaded: {file.filename}"
    }

@app.post("/upload-csv")
def upload_csv_file(file: UploadFile = File(...), user_id: int = Depends(get_current_user)):

    uploads_dir = Path("uploads")

    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / file.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    session_id = SessionManager.create_session(
      user_id=user_id,
      db_type="sqlite",
      db_config={
          "path": str(file_path)
       }
    )
    schema_key = SchemaCache.create_key(
       "sqlite",
       str(file_path)
   )

    SchemaCache.invalidate(
      schema_key
    )
    return {
        "success": True,
        "session_id": session_id,
        "message": f"CSV uploaded: {file.filename}"
    }

class PostgreSQLConnectionRequest(BaseModel):

    host: str
    port: int
    database: str
    username: str
    password: str

@app.post("/connect-postgresql")
def connect_postgresql(
    request: PostgreSQLConnectionRequest,
    user_id: int = Depends(get_current_user)
    ):

    session_id = SessionManager.create_session(
       user_id=user_id,
       db_type="postgresql",
       db_config={
          "host": request.host,
          "port": request.port,
          "database": request.database,
          "username": request.username,
           "password": request.password
        }
    )
    schema_key = SchemaCache.create_key(
       "postgresql",
       request.database
   )

    SchemaCache.invalidate(
      schema_key
    )
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Connected to PostgreSQL"
    }

class MySQLConnectionRequest(BaseModel):

    host: str
    port: int
    database: str
    username: str
    password: str

@app.post("/connect-mysql")
def connect_mysql(
    request: MySQLConnectionRequest,
    user_id: int = Depends(get_current_user)
):

    session_id = SessionManager.create_session(
    user_id=user_id,
    db_type="mysql",
    db_config={
         "host": request.host,
         "port": request.port,
         "database": request.database,
         "username": request.username,
         "password": request.password
        }
    )
    schema_key = SchemaCache.create_key(
       "mysql",
       request.database
   )

    SchemaCache.invalidate(
      schema_key
    )
    return {
        "success": True,
        "session_id": session_id,
        "message": "Connected to MySQL"
    }