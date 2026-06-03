from backend.app.inference.sql_generator import SQLGenerator
from backend.app.security.sql_validator import SQLValidator

from backend.database.universal_schema_extractor import (
    UniversalSchemaExtractor
)

from backend.database.universal_query_executor import (
    UniversalQueryExecutor
)


class TextToSQLPipeline:

    def __init__(self):

        print("Initializing Text-to-SQL Pipeline...")

        self.sql_generator = SQLGenerator()

        self.conversation_history = []

        print("Pipeline initialized successfully!")

    def run(
        self,
        question: str,
        engine
    ):

        # =========================
        # STEP 1 — EXTRACT SCHEMA
        # =========================

        schema_extractor = UniversalSchemaExtractor(
            engine
        )

        schema = schema_extractor.get_schema()

        # =========================
        # STEP 2 — GENERATE SQL
        # =========================

        sql_query = self.sql_generator.generate_sql(
            schema=schema,
            question=question,
            conversation_history=self.conversation_history
        )

        # =========================
        # STEP 3 — VALIDATE SQL
        # =========================

        validation = SQLValidator.validate(
            sql_query
        )

        if not validation["safe"]:

            return {
                "question": question,
                "generated_sql": sql_query,
                "execution_result": {
                    "success": False,
                    "error": validation["reason"]
                }
            }

        # =========================
        # STEP 4 — EXECUTE SQL
        # =========================

        query_executor = UniversalQueryExecutor(
            engine
        )

        execution_result = query_executor.execute_query(
            sql_query
        )

        # =========================
        # STEP 5 — UPDATE MEMORY
        # =========================

        self.conversation_history.append({
            "question": question,
            "sql": sql_query
        })

        # =========================
        # FINAL RESPONSE
        # =========================

        return {
            "question": question,
            "generated_sql": sql_query,
            "execution_result": execution_result
        }

