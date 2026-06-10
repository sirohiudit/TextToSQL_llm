import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "cleaned_dataset.json"

OUTPUT_FILE = PROCESSED_DIR / "dialect_augmented_dataset.json"


# ==================================================
# DETECT SQLITE SPECIFIC FUNCTIONS
# ==================================================

SQLITE_PATTERNS = [
    r"strftime\s*\(",
    r"date\s*\(",
    r"datetime\s*\(",
    r"julianday\s*\(",
    r"time\s*\(",
    r"substr\s*\(",
    r"ifnull\s*\(",
    r"coalesce\s*\(",
    r"length\s*\(",
    r"lower\s*\(",
    r"upper\s*\(",
]


def contains_sqlite_function(sql):

    sql_lower = sql.lower()

    for pattern in SQLITE_PATTERNS:

        if re.search(pattern, sql_lower):

            return True

    return False


# ==================================================
# SQLITE -> POSTGRESQL
# ==================================================

def sqlite_to_postgresql(sql):

    converted = sql

    # DATE FUNCTIONS

    converted = re.sub(
        r"strftime\('%Y-%m',\s*([^)]+)\)",
        r"date_trunc('month', \1)",
        converted,
        flags=re.IGNORECASE
    )

    converted = re.sub(
        r"strftime\('%Y',\s*([^)]+)\)",
        r"EXTRACT(YEAR FROM \1)",
        converted,
        flags=re.IGNORECASE
    )

    converted = re.sub(
        r"strftime\('%m',\s*([^)]+)\)",
        r"EXTRACT(MONTH FROM \1)",
        converted,
        flags=re.IGNORECASE
    )

    # STRING FUNCTIONS

    converted = re.sub(
        r"substr\s*\(",
        "substring(",
        converted,
        flags=re.IGNORECASE
    )
    
    # NULL FUNCTIONS

    converted = re.sub(
        r"ifnull\s*\(",
        "COALESCE(",
        converted,
        flags=re.IGNORECASE
    )

    return converted


# ==================================================
# SQLITE -> MYSQL
# ==================================================

def sqlite_to_mysql(sql):

    converted = sql

    # =====================================
    # DATE FUNCTIONS
    # =====================================

    converted = re.sub(
        r"strftime\('%Y-%m',\s*([^)]+)\)",
        r"DATE_FORMAT(\1, '%Y-%m')",
        converted,
        flags=re.IGNORECASE
    )

    converted = re.sub(
        r"strftime\('%Y',\s*([^)]+)\)",
        r"YEAR(\1)",
        converted,
        flags=re.IGNORECASE
    )

    converted = re.sub(
        r"strftime\('%m',\s*([^)]+)\)",
        r"MONTH(\1)",
        converted,
        flags=re.IGNORECASE
    )

    # =====================================
    # STRING FUNCTIONS
    # =====================================

    converted = re.sub(
        r"substr\s*\(",
        "SUBSTRING(",
        converted,
        flags=re.IGNORECASE
    )

    # =====================================
    # NULL FUNCTIONS
    # =====================================

    converted = re.sub(
        r"ifnull\s*\(",
        "IFNULL(",
        converted,
        flags=re.IGNORECASE
    )

    return converted


# ==================================================
# MAIN
# ==================================================

def main():

    print("\nLoading cleaned dataset...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        dataset = json.load(f)

    augmented = []

    sqlite_count = 0
    postgres_count = 0
    mysql_count = 0

    for example in dataset:

        sql = example["response"]

        # =====================================
        # KEEP ORIGINAL SQLITE SAMPLE
        # =====================================

        augmented.append(example)

        sqlite_count += 1

        # =====================================
        # ONLY AUGMENT DIALECT-SPECIFIC SQL
        # =====================================

        if not contains_sqlite_function(sql):

            continue

        # =====================================
        # POSTGRESQL VERSION
        # =====================================

        postgres_example = example.copy()

        postgres_example["database_type"] = "PostgreSQL"

        postgres_example["prompt"] = example["prompt"].replace(
            "### DATABASE TYPE:\nSQLite",
            "### DATABASE TYPE:\nPostgreSQL"
        )

        postgres_example["response"] = sqlite_to_postgresql(sql)

        augmented.append(postgres_example)

        postgres_count += 1

        # =====================================
        # MYSQL VERSION
        # =====================================

        mysql_example = example.copy()

        mysql_example["database_type"] = "MySQL"

        mysql_example["prompt"] = example["prompt"].replace(
            "### DATABASE TYPE:\nSQLite",
            "### DATABASE TYPE:\nMySQL"
        )

        mysql_example["response"] = sqlite_to_mysql(sql)

        augmented.append(mysql_example)

        mysql_count += 1

    print("\nSaving augmented dataset...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            augmented,
            f,
            indent=2
        )

    print("\n" + "=" * 50)

    print(f"Original SQLite Samples: {sqlite_count}")

    print(f"PostgreSQL Variants: {postgres_count}")

    print(f"MySQL Variants: {mysql_count}")

    print(f"Final Dataset Size: {len(augmented)}")

    print("=" * 50)

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":

    main()