from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import UploadFile, File
import shutil
from pathlib import Path

from backend.database.database_manager import DatabaseManager
from backend.app.text_to_sql_pipeline import TextToSQLPipeline


app = FastAPI(
    title="Text-to-SQL AI API"
)


# =====================================
# LOAD PIPELINE
# =====================================

pipeline = TextToSQLPipeline()

db_manager = DatabaseManager()

current_engine = None
# =====================================
# REQUEST MODEL
# =====================================

class QueryRequest(BaseModel):

    question: str


# =====================================
# ROOT ENDPOINT
# =====================================

@app.get("/")
def root():

    return {
        "message": "Text-to-SQL API is running!"
    }


# =====================================
# ASK ENDPOINT
# =====================================

@app.post("/ask")
def ask_question(request: QueryRequest):

    global current_engine

    if current_engine is None:

        return {
            "success": False,
            "error": "No database connected."
        }

    response = pipeline.run(
        request.question,
        current_engine
    )

    return response

@app.post("/upload-sqlite")
def upload_sqlite_db(file: UploadFile = File(...)):

    global current_engine

    uploads_dir = Path("uploads")

    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / file.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Connect database
    db_manager.connect_sqlite(
        str(file_path)
    )

    current_engine = db_manager.get_engine()

    return {
        "success": True,
        "message": f"SQLite database uploaded: {file.filename}"
    }

@app.post("/upload-csv")
def upload_csv_file(file: UploadFile = File(...)):

    global current_engine

    uploads_dir = Path("uploads")

    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / file.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    db_manager.connect_csv(
        str(file_path)
    )

    current_engine = db_manager.get_engine()

    return {
        "success": True,
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
    request: PostgreSQLConnectionRequest
):

    global current_engine

    db_manager.connect_postgresql(
        host=request.host,
        port=request.port,
        database=request.database,
        username=request.username,
        password=request.password
    )

    current_engine = db_manager.get_engine()

    return {
        "success": True,
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
    request: MySQLConnectionRequest
):

    global current_engine

    db_manager.connect_mysql(
        host=request.host,
        port=request.port,
        database=request.database,
        username=request.username,
        password=request.password
    )

    current_engine = db_manager.get_engine()

    return {
        "success": True,
        "message": "Connected to MySQL"
    }