import json

from backend.app.cache.redis_client import redis_client


class SessionCache:

    TTL = 86400

    @staticmethod
    def get(session_id):

        data = redis_client.get(
            f"session:{session_id}"
        )

        if not data:
            return None

        return json.loads(data)

    @staticmethod
    def set(
        session_id,
        session_data
    ):

        redis_client.setex(
            f"session:{session_id}",
            SessionCache.TTL,
            json.dumps(session_data)
        )