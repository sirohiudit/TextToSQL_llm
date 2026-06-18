import sqlite3

DB_PATH = r"C:\projects\Text_to_SQL_llm\backend\database\user_data\auth.db"


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

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO query_history(
                user_id,
                session_id,
                question,
                generated_sql,
                database_type,
                execution_time,
                success
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                user_id,
                session_id,
                question,
                generated_sql,
                database_type,
                execution_time,
                int(success)
            )
        )

        conn.commit()

        conn.close()

    @staticmethod
    def get_user_history(
        user_id
    ):

        conn = sqlite3.connect(DB_PATH)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        rows = cursor.execute(
            """
            SELECT *
            FROM query_history
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT 100
            """,
            (user_id,)
        ).fetchall()

        conn.close()

        return [dict(row) for row in rows]