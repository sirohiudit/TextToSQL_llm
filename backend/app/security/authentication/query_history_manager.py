from sqlalchemy import text

from backend.database.auth_db import engine


class QueryHistoryManager:

    @staticmethod
    def save_query(
        user_id,
        session_id,
        question,
        generated_sql,
        database_type,
        execution_time,
        success
    ):

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO query_history(
                        user_id,
                        session_id,
                        question,
                        generated_sql,
                        database_type,
                        execution_time,
                        success
                    )
                    VALUES(
                        :user_id,
                        :session_id,
                        :question,
                        :generated_sql,
                        :database_type,
                        :execution_time,
                        :success
                    )
                """),
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "question": question,
                    "generated_sql": generated_sql,
                    "database_type": database_type,
                    "execution_time": execution_time,
                    "success": success
                }
            )

    @staticmethod
    def get_user_history(
        user_id
    ):

        with engine.begin() as conn:

            rows = conn.execute(
                text("""
                    SELECT *
                    FROM query_history
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                    LIMIT 100
                """),
                {
                    "user_id": user_id
                }
            ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def get_session_history(
        session_id
    ):

        with engine.begin() as conn:

            rows = conn.execute(
                text("""
                    SELECT *
                    FROM query_history
                    WHERE session_id = :session_id
                    ORDER BY created_at DESC
                """),
                {
                    "session_id": session_id
                }
            ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    @staticmethod
    def delete_history(
        user_id
    ):

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE FROM query_history
                    WHERE user_id = :user_id
                """),
                {
                    "user_id": user_id
                }
            )