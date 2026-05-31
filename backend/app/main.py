from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.text_to_sql_pipeline import TextToSQLPipeline


app = FastAPI(
    title="Text-to-SQL AI API"
)


# =====================================
# LOAD PIPELINE
# =====================================

pipeline = TextToSQLPipeline()


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

    response = pipeline.run(
        request.question
    )

    return response