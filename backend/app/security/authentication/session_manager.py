from sqlalchemy import text
import json
from datetime import datetime
from backend.app.cache.session_cache import SessionCache
from backend.database.auth_db import engine

class SessionManager:

    @staticmethod
    def create_session(
        user_id,
        db_type,
        db_config
    ):

        with engine.begin() as conn:

            result = conn.execute(
                text("""
                    INSERT INTO sessions(
                        user_id,
                        db_type,
                        db_config,
                        conversation_history
                    )
                    VALUES(
                        :user_id,
                        :db_type,
                        :db_config,
                        :conversation_history
                    )
                    RETURNING id
                """),
                {
                    "user_id": user_id,
                    "db_type": db_type,
                    "db_config": json.dumps(db_config),
                    "conversation_history": "[]"
                }
            )
            row = result.fetchone()
            if row is None:
                raise RuntimeError("Failed to create session and retrieve its id")
            session_id = row[0]

        return session_id

    @staticmethod
    def get_session(
        session_id,
        user_id
    ):

        cached = SessionCache.get(session_id)

        if cached:
            return cached

        with engine.begin() as conn:

            row = conn.execute(
                text("""
                    SELECT *
                    FROM sessions
                    WHERE id = :session_id
                    AND user_id = :user_id
                """),
                {
                    "session_id": session_id,
                    "user_id": user_id
                }
            ).mappings().first()

        if row is None:
            return None

        session_data = {
            "id": row["id"],
            "user_id": row["user_id"],
            "db_type": row["db_type"],
            "db_config": json.loads(
                row["db_config"]
            ),
            "conversation_history": json.loads(
                row["conversation_history"]
            )
        }

        SessionCache.set(
            session_id,
            session_data
        )

        return session_data    
    
    @staticmethod
    def update_history(
        session_id,
        history
    ):

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE sessions
                    SET
                        conversation_history = :history,
                        last_activity = :last_activity
                    WHERE id = :session_id
                """),
                {
                    "history": json.dumps(history),
                    "last_activity": datetime.utcnow(),
                    "session_id": session_id
                }
            )

        cached = SessionCache.get(
            session_id
        )

        if cached:

            cached[
                "conversation_history"
            ] = history

            SessionCache.set(
                session_id,
                cached
            )
    @staticmethod
    def delete_session(
        session_id,
        user_id
    ):

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE FROM sessions
                    WHERE id = :session_id
                    AND user_id = :user_id
                """),
                {
                    "session_id": session_id,
                    "user_id": user_id
                }
            )        