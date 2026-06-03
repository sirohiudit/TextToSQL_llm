import pandas as pd


class UniversalQueryExecutor:

    def __init__(self, engine):

        self.engine = engine

    def execute_query(self, sql_query: str):

        try:

            df = pd.read_sql(
                sql_query,
                self.engine
            )

            return {
                "success": True,
                "results": df.to_dict(
                    orient="records"
                ),
                "row_count": len(df)
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }