from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    
else:
    print(".env file not found - using system environment variables")

# Validate required variables
def get_required_env_var(var_name: str, default=None):
    """Get environment variable with optional validation"""
    value = os.getenv(var_name, default)
    if not value:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    return value


SECRET_KEY = get_required_env_var("SECRET_KEY")

ALGORITHM = get_required_env_var("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(get_required_env_var("ACCESS_TOKEN_EXPIRE_MINUTES"))


pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_access_token(user_id: int):

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_token(token: str):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )