import hashlib

from .redis_client import redis_client


class SchemaCache:

    TTL = 3600

    @staticmethod
    def create_key(
        db_type,
        db_config
    ):

        raw = (
            db_type +
            str(db_config)
        )

        return hashlib.sha256(
            raw.encode()
        ).hexdigest()

    @staticmethod
    def get(key):

        return redis_client.get(
            f"schema:{key}"
        )

    @staticmethod
    def set(
        key,
        schema
    ):

        redis_client.setex(
            f"schema:{key}",
            SchemaCache.TTL,
            schema
        )
    @staticmethod
    def invalidate(key):

        redis_client.delete(
        f"schema:{key}"
    )   