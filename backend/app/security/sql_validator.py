class SQLValidator:

    ALLOWED_STATEMENTS = [
        "SELECT"
    ]

    BLOCKED_KEYWORDS = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "REPLACE"
    ]

    @staticmethod
    def validate(sql_query: str):

        sql_upper = sql_query.upper().strip()

        # =====================================
        # MUST START WITH SELECT
        # =====================================

        if not sql_upper.startswith("SELECT"):

            return {
                "safe": False,
                "reason": "Only SELECT queries are allowed."
            }

        # =====================================
        # BLOCK DANGEROUS KEYWORDS
        # =====================================

        for keyword in SQLValidator.BLOCKED_KEYWORDS:

            if keyword in sql_upper:

                return {
                    "safe": False,
                    "reason": f"Blocked keyword detected: {keyword}"
                }

        return {
            "safe": True,
            "reason": "Query is safe."
        }