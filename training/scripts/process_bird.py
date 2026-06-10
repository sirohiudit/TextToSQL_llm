import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

BIRD_DIR = BASE_DIR / "data" / "raw" / "bird_data"

DATABASES_DIR = BIRD_DIR / "train_databases"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# EXTRACT SQLITE SCHEMA
# ==========================================

def extract_schema(db_path):

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
    """)

    tables = cursor.fetchall()

    conn.close()

    schema_parts = []

    for table in tables:

        if table[0]:

            schema_parts.append(
                table[0]
            )

    return "\n\n".join(schema_parts)


# ==========================================
# BUILD PROMPT
# ==========================================

def build_prompt(
    schema,
    question,
    evidence
):

    return f"""### DATABASE TYPE:
SQLite

### DATABASE SCHEMA:
{schema}

### EVIDENCE:
{evidence}

### QUESTION:
{question}

### SQL:
"""


# ==========================================
# MAIN
# ==========================================

def main():

    train_path = BIRD_DIR / "train.json"

    with open(
        train_path,
        "r",
        encoding="utf-8"
    ) as f:

        bird_examples = json.load(f)

    processed_examples = []

    total = len(bird_examples)

    print(f"\nProcessing {total} BIRD examples...\n")

    for idx, example in enumerate(bird_examples):

        db_id = example["db_id"]

        question = example["question"]

        evidence = example.get(
            "evidence",
            ""
        )

        sql = example["SQL"].strip()

        db_path = (
            DATABASES_DIR
            / db_id
            / f"{db_id}.sqlite"
        )

        if not db_path.exists():

            continue

        schema = extract_schema(
            db_path
        )

        prompt = build_prompt(
            schema=schema,
            question=question,
            evidence=evidence
        )

        processed_examples.append({

            "database_type": "SQLite",

            "prompt": prompt,

            "response": sql

        })

        if idx % 500 == 0:

            print(
                f"{idx}/{total}"
            )

    output_path = (
        OUTPUT_DIR
        / "bird_processed.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed_examples,
            f,
            indent=2
        )

    print("\n" + "=" * 50)

    print(
        f"Saved {len(processed_examples)} BIRD examples"
    )

    print("=" * 50)


if __name__ == "__main__":

    main()