import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"


class SchemaExtractor:

    def __init__(self):

        self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)

    def get_schema(self):

        cursor = self.connection.cursor()

        # Get all tables
        cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
        """)

        tables = cursor.fetchall()

        schema = ""

        for table in tables:

            table_name = table[0]

            if table_name == "sqlite_sequence":
                continue

            schema += f"\nCREATE TABLE {table_name} (\n"

            cursor.execute(f"""
            PRAGMA table_info({table_name});
            """)

            columns = cursor.fetchall()

            column_definitions = []

            for column in columns:

                col_name = column[1]
                col_type = column[2]

                column_definitions.append(
                    f"    {col_name} {col_type}"
                )

            schema += ",\n".join(column_definitions)

            schema += "\n);\n"

        return schema

    def close(self):

        self.connection.close()