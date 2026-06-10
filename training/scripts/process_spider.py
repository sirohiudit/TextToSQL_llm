import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SPIDER_DIR = BASE_DIR / "data" / "raw" / "spider_data"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_schema(db_id, tables_data):

    schema_lines = []

    table_names = tables_data["table_names_original"]

    column_names = tables_data["column_names_original"]

    column_types = tables_data["column_types"]

    table_columns = {}

    for idx, (table_idx, column_name) in enumerate(column_names):

        if table_idx == -1:
            continue

        table_name = table_names[table_idx]

        if table_name not in table_columns:
            table_columns[table_name] = []

        col_type = column_types[idx]

        table_columns[table_name].append(
            f"{column_name} {col_type}"
        )

    for table_name, columns in table_columns.items():

        schema = f"CREATE TABLE {table_name} (\n"
        schema += ",\n".join(columns)
        schema += "\n);"

        schema_lines.append(schema)

    return "\n\n".join(schema_lines)


def build_prompt(schema, question, database_type="SQLite"):

    return f"""### DATABASE TYPE:
{database_type}

### DATABASE SCHEMA:
{schema}

### QUESTION:
{question}

### SQL:
"""


def main():

    train_path = SPIDER_DIR / "train_spider.json"

    tables_path = SPIDER_DIR / "tables.json"

    with open(train_path, "r", encoding="utf-8") as f:
        spider_examples = json.load(f)

    with open(tables_path, "r", encoding="utf-8") as f:
        tables = json.load(f)

    tables_map = {}

    for table in tables:
        tables_map[table["db_id"]] = table

    processed_examples = []

    for example in spider_examples:

        question = example["question"]

        sql = example["query"]

        db_id = example["db_id"]

        schema = build_schema(
            db_id,
            tables_map[db_id]
        )

        prompt = build_prompt(
            schema= schema,
            question=question,
            database_type="SQLite"
        )

        processed_examples.append({
            "database_type": "SQLite",
            "prompt": prompt,
            "response": sql
        })

    output_path = OUTPUT_DIR / "spider_processed.json"

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(processed_examples, f, indent=2)

    print(f"\nSaved {len(processed_examples)} Spider examples")


if __name__ == "__main__":

    main()