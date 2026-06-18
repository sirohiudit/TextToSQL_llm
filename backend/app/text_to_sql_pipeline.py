from backend.app.inference.sql_generator import SQLGenerator
from backend.app.security.sql_validator import SQLValidator

from backend.database.universal_schema_extractor import (
    UniversalSchemaExtractor
)

from backend.database.universal_query_executor import (
    UniversalQueryExecutor
)
from backend.database.sql_dialect_converter import (
    SQLDialectConverter
)
from backend.app.cache.schema_cache import (
    SchemaCache
)
from backend.app.cache.prompt_cache import (
    PromptCache
)


class TextToSQLPipeline:

    def __init__(self):

        print("Initializing Text-to-SQL Pipeline...")

        self.sql_generator = SQLGenerator()

        print("Pipeline initialized successfully!")

    def run(
        self,
        question: str,
        engine,
        database_type,
        conversation_history=None
    ):
        if conversation_history is None:
            conversation_history = []
        # =========================
        # STEP 1 — EXTRACT SCHEMA
        # =========================

        schema_key = SchemaCache.create_key(
          database_type,
         str(engine.url)
        )

        schema = SchemaCache.get(
          schema_key
        )

        if schema is None:

         schema_extractor = (UniversalSchemaExtractor(engine )  )

         schema = (schema_extractor.get_schema())

         SchemaCache.set(
             schema_key,
             schema
            )

        # =========================
        # STEP 2 — GENERATE SQL
        # =========================

        prompt_key = PromptCache.create_key(
           question,
           schema
        )

        cached = PromptCache.get(
           prompt_key
        )

        if cached:

          canonical_sql = cached[
              "canonical_sql"
            ]

        else:

          canonical_sql = (
             self.sql_generator.generate_sql(
                 schema=schema,
                 question=question,
                 database_type="SQLite",
                  conversation_history=conversation_history
                )
            )

          PromptCache.set(
              prompt_key,
              {
              "canonical_sql": canonical_sql
              }
            )
        sql_query = SQLDialectConverter.convert(
             canonical_sql,
             database_type
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
                "conversation_history": conversation_history,
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

        # ===================================
        # QUERY REPAIR
        # ===================================

        if not execution_result["success"]:

           try:

              repaired_sql = self.sql_generator.repair_sql(
              question=question,
              failed_sql=sql_query,
              error_message=execution_result["error"],
              schema=schema
           )

              repair_validation = SQLValidator.validate(
                  repaired_sql
                )

              if repair_validation["safe"]:

                  repaired_result = query_executor.execute_query(
                     repaired_sql
                    )

                  if repaired_result["success"]:

                     sql_query = repaired_sql

                     execution_result = repaired_result

           except Exception as e:

               print(
                  "Repair failed:",
                 str(e)
                )



        # =========================
        # STEP 5 — UPDATE MEMORY
        # =========================
        updated_history = conversation_history.copy()

        updated_history.append(
            {
                "question": question,
                "sql": sql_query
            }
        )
        updated_history = updated_history[-20:]

        # =========================
        # FINAL RESPONSE
        # =========================

        return {
            "question": question,
            "database_type": database_type,
            "canonical_sql": canonical_sql,
            "generated_sql": sql_query,
            "conversation_history": updated_history,
            "execution_result": execution_result,
            "query_repaired": ( execution_result["success"] and sql_query != canonical_sql )
        }

