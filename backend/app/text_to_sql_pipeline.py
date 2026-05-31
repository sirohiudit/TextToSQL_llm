from backend.app.inference.sql_generator import SQLGenerator
from backend.database.schema_extractor import SchemaExtractor
from backend.database.query_executor import QueryExecutor


class TextToSQLPipeline:

    def __init__(self):

        print("Initializing Text-to-SQL Pipeline...")

        self.schema_extractor = SchemaExtractor()

        self.sql_generator = SQLGenerator()

        self.query_executor = QueryExecutor()

        print("Pipeline initialized successfully!")

    def run(self, question: str):

        # =========================
        # STEP 1 — EXTRACT SCHEMA
        # =========================

        schema = self.schema_extractor.get_schema()

        # =========================
        # STEP 2 — GENERATE SQL
        # =========================

        sql_query = self.sql_generator.generate_sql(
            schema=schema,
            question=question
        )

        # =========================
        # STEP 3 — EXECUTE SQL
        # =========================

        execution_result = self.query_executor.execute_query(
            sql_query
        )

        # =========================
        # FINAL RESPONSE
        # =========================

        return {
            "question": question,
            "generated_sql": sql_query,
            "execution_result": execution_result
        }

    def close(self):

        self.schema_extractor.close()

        self.query_executor.close()