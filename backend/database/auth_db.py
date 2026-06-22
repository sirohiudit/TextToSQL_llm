from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Read the Postgres connection URL from environment
DATABASE_URL = os.getenv("POSTGRES_DB")
if not DATABASE_URL:
    raise RuntimeError("POSTGRES_DB environment variable is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)