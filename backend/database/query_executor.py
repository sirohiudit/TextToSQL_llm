import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

print("BASE_DIR:", BASE_DIR)
print("DB_PATH:", DB_PATH)
print("DB EXISTS:", DB_PATH.exists())


class QueryExecutor:

    def __init__(self):

        self.connection = sqlite3.connect(DB_PATH,check_same_thread=False)

        self.connection.row_factory = sqlite3.Row

    def execute_query(self, sql_query: str):

        try:

            cursor = self.connection.cursor()

            cursor.execute(sql_query)

            rows = cursor.fetchall()

            results = [
                dict(row)
                for row in rows
            ]

            return {
                "success": True,
                "results": results,
                "row_count": len(results)
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def close(self):

        self.connection.close()