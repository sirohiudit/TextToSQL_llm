import hashlib
import json

from .redis_client import redis_client


class RepairCache:

    TTL = 3600

    @staticmethod
    def create_key(
        failed_sql,
        error
    ):

        raw = failed_sql + error

        return hashlib.sha256(
            raw.encode()
        ).hexdigest()

    @staticmethod
    def get(key):

        value = redis_client.get(
            f"repair:{key}"
        )

        if value:

            return json.loads(value)

        return None

    @staticmethod
    def set(
        key,
        value
    ):

        redis_client.setex(
            f"repair:{key}",
            RepairCache.TTL,
            json.dumps(value)
        )