import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

WIKISQL_DIR = BASE_DIR / "data" / "raw" / "wikisql_data"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


AGG_OPS = [
    "",
    "MAX",
    "MIN",
    "COUNT",
    "SUM",
    "AVG"
]

COND_OPS = [
    "=",
    ">",
    "<"
]


# ==========================================
# BUILD SQL FROM STRUCTURED FORMAT
# ==========================================

def build_sql(sql_data, table_data):

    headers = table_data["header"]

    table_name = table_data["id"]

    # =========================
    # SELECT COLUMN
    # =========================

    select_column = headers[
        sql_data["sel"]
    ]

    agg = AGG_OPS[
        sql_data["agg"]
    ]

    if agg:

        select_part = f"{agg}({select_column})"

    else:

        select_part = select_column

    # =========================
    # WHERE CONDITIONS
    # =========================

    where_clauses = []

    for cond in sql_data["conds"]:

        column_index, operator_index, value = cond

        column_name = headers[column_index]

        operator = COND_OPS[operator_index]

        where_clauses.append(
            f'{column_name} {operator} "{value}"'
        )

    sql = f"SELECT {select_part} FROM {table_name}"

    if where_clauses:

        sql += " WHERE "

        sql += " AND ".join(where_clauses)

    sql += ";"

    return sql


# ==========================================
# BUILD SCHEMA
# ==========================================

def build_schema(table_data):

    table_name = table_data["id"]

    headers = table_data["header"]

    types = table_data["types"]

    columns = []

    for h, t in zip(headers, types):

        columns.append(f"{h} {t}")

    schema = f"CREATE TABLE {table_name} (\n"

    schema += ",\n".join(columns)

    schema += "\n);"

    return schema


# ==========================================
# BUILD PROMPT
# ==========================================

def build_prompt(
    schema,
    question,
    database_type="SQLite"
):

    return f"""### DATABASE TYPE:
{database_type}

### DATABASE SCHEMA:
{schema}

### QUESTION:
{question}

### SQL:
"""


# ==========================================
# PROCESS SPLIT
# ==========================================

def process_split(split_name):

    examples = []

    jsonl_path = WIKISQL_DIR / f"{split_name}.jsonl"

    tables_path = WIKISQL_DIR / f"{split_name}.tables.jsonl"

    # =========================
    # LOAD TABLES
    # =========================

    tables = {}

    with open(tables_path, "r", encoding="utf-8") as f:

        for line in f:

            table = json.loads(line)

            tables[table["id"]] = table

    # =========================
    # LOAD EXAMPLES
    # =========================

    with open(jsonl_path, "r", encoding="utf-8") as f:

        for line in f:

            example = json.loads(line)

            question = example["question"]

            sql_data = example["sql"]

            table_id = example["table_id"]

            table_data = tables[table_id]

            # =========================
            # BUILD SQL
            # =========================

            sql = build_sql(
                sql_data,
                table_data
            )

            # =========================
            # BUILD SCHEMA
            # =========================

            schema = build_schema(
                table_data
            )

            # =========================
            # BUILD PROMPT
            # =========================

            prompt = build_prompt(
              schema=schema,
              question=question,
              database_type="SQLite"
            )

            examples.append({
                "database_type": "SQLite",
                "prompt": prompt,
                "response": sql
            })

    return examples


# ==========================================
# MAIN
# ==========================================

def main():

    all_examples = []

    for split in ["train", "dev", "test"]:

        print(f"\nProcessing WikiSQL {split}...")

        split_examples = process_split(split)

        all_examples.extend(split_examples)

        print(f"Added {len(split_examples)} examples")

    output_path = OUTPUT_DIR / "wikisql_processed.json"

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(all_examples, f, indent=2)

    print(f"\nSaved {len(all_examples)} WikiSQL examples")


if __name__ == "__main__":

    main()