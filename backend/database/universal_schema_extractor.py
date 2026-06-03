from sqlalchemy import inspect


class UniversalSchemaExtractor:

    def __init__(self, engine):

        self.engine = engine

        self.inspector = inspect(engine)

    def get_schema(self):

        schema = ""

        tables = self.inspector.get_table_names()

        for table_name in tables:

            schema += f"\nCREATE TABLE {table_name} (\n"

            columns = self.inspector.get_columns(table_name)

            column_defs = []

            for column in columns:

                col_name = column["name"]

                col_type = str(column["type"])

                column_defs.append(
                    f"    {col_name} {col_type}"
                )

            schema += ",\n".join(column_defs)

            schema += "\n);\n"

        return schema