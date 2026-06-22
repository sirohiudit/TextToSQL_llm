import redis
from dotenv import load_dotenv, find_dotenv
import os


# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

def get_required_env_var(var_name: str, default=None):
    """Get environment variable with optional validation"""
    value = os.getenv(var_name, default)
    if not value:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    return value

# Load Redis configuration from environment
REDIS_HOST = get_required_env_var("REDIS_HOST")
REDIS_PORT = int(get_required_env_var("REDIS_PORT"))

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)