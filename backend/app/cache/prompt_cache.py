import hashlib
import json

from .redis_client import redis_client


class PromptCache:

    TTL = 3600

    @staticmethod
    def create_key(
        question,
        schema
    ):
        schema_hash = hashlib.sha256(
            schema.encode()
        ).hexdigest()

        raw = (
            question +
            schema_hash
        )

        return hashlib.sha256(
            raw.encode()
        ).hexdigest()

    @staticmethod
    def get(key):

        result = redis_client.get(
            f"prompt:{key}"
        )

        if not result:
            return None

        return json.loads(result)

    @staticmethod
    def set(
        key,
        value
    ):

        redis_client.setex(
            f"prompt:{key}",
            PromptCache.TTL,
            json.dumps(value)
        )