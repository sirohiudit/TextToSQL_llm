import sqlite3
import json
from datetime import datetime
from backend.app.cache.session_cache import SessionCache

DB_PATH = r"C:\projects\Text_to_SQL_llm\backend\database\user_data\auth.db"


class SessionManager:

    @staticmethod
    def create_session(
        user_id,
        db_type,
        db_config
    ):

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sessions(
                user_id,
                db_type,
                db_config,
                conversation_history
            )
            VALUES(?,?,?,?)
            """,
            (
                user_id,
                db_type,
                json.dumps(db_config),
                "[]"
            )
        )

        conn.commit()

        session_id = cursor.lastrowid

        conn.close()

        return session_id

    @staticmethod
    def get_session(
        session_id,
        user_id
    ):
        cached = SessionCache.get(session_id)

        if cached:
          return cached

        conn = sqlite3.connect(DB_PATH)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        row = cursor.execute(
            """
            SELECT *
            FROM sessions
            WHERE id=?
            AND user_id=?
            """,
            (
                session_id,
                user_id
            )
        ).fetchone()

        conn.close()

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

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE sessions

            SET conversation_history=?,
                last_activity=?
            WHERE id=?
            """,
            (
                json.dumps(history),
                datetime.utcnow(),
                session_id
            )
        )

        conn.commit()

        conn.close()
        cached = SessionCache.get(
           session_id
        )

        if cached:

         cached["conversation_history"] = history

         SessionCache.set(
            session_id,
            cached
        )