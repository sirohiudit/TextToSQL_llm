import re


class SQLDialectConverter:

    @staticmethod
    def convert(sql: str, database_type: str) -> str:

        if not sql:
            return sql

        database_type = database_type.lower()

        if database_type == "sqlite":
            return sql

        if database_type == "postgresql":
            return SQLDialectConverter.sqlite_to_postgresql(sql)

        if database_type == "mysql":
            return SQLDialectConverter.sqlite_to_mysql(sql)

        return sql

    # ==================================================
    # SQLITE → POSTGRESQL
    # ==================================================

    @staticmethod
    def sqlite_to_postgresql(sql: str) -> str:

        converted = sql

        # ------------------------------------------
        # strftime('%Y-%m', column)
        # -> to_char(column, 'YYYY-MM')
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%Y-%m'\s*,\s*([^)]+)\)",
            r"to_char(\1, 'YYYY-MM')",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # strftime('%Y', column)
        # -> EXTRACT(YEAR FROM column)
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%Y'\s*,\s*([^)]+)\)",
            r"EXTRACT(YEAR FROM \1)",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # strftime('%m', column)
        # -> EXTRACT(MONTH FROM column)
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%m'\s*,\s*([^)]+)\)",
            r"EXTRACT(MONTH FROM \1)",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # ifnull(x,y)
        # -> coalesce(x,y)
        # ------------------------------------------

        converted = re.sub(
            r"\bifnull\s*\(",
            "coalesce(",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # substr()
        # -> substring()
        # ------------------------------------------

        converted = re.sub(
            r"\bsubstr\s*\(",
            "substring(",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # Random()
        # ------------------------------------------

        converted = re.sub(
            r"\brandom\s*\(\s*\)",
            "RANDOM()",
            converted,
            flags=re.IGNORECASE,
        )

        return converted

    # ==================================================
    # SQLITE → MYSQL
    # ==================================================

    @staticmethod
    def sqlite_to_mysql(sql: str) -> str:

        converted = sql

        # ------------------------------------------
        # strftime('%Y-%m', column)
        # -> DATE_FORMAT(column,'%Y-%m')
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%Y-%m'\s*,\s*([^)]+)\)",
            r"DATE_FORMAT(\1, '%Y-%m')",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # strftime('%Y', column)
        # -> YEAR(column)
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%Y'\s*,\s*([^)]+)\)",
            r"YEAR(\1)",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # strftime('%m', column)
        # -> MONTH(column)
        # ------------------------------------------

        converted = re.sub(
            r"strftime\s*\(\s*'%m'\s*,\s*([^)]+)\)",
            r"MONTH(\1)",
            converted,
            flags=re.IGNORECASE,
        )

        # ------------------------------------------
        # ifnull()
        # MySQL already supports IFNULL
        # ------------------------------------------

        # ------------------------------------------
        # substr()
        # -> substring()
        # ------------------------------------------

        converted = re.sub(
            r"\bsubstr\s*\(",
            "substring(",
            converted,
            flags=re.IGNORECASE,
        )

        return converted