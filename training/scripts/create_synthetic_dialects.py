import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "dialect_augmented_dataset.json"

OUTPUT_FILE = PROCESSED_DIR / "final_multidialect_dataset.json"


# ==========================================
# CONFIG
# ==========================================

POSTGRES_SAMPLES = 5000
MYSQL_SAMPLES = 5000

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nLoading dataset...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:

        dataset = json.load(f)

    print(f"Loaded {len(dataset)} examples")

    # =====================================
    # KEEP EXISTING DATA
    # =====================================

    final_dataset = list(dataset)

    # =====================================
    # ONLY SAMPLE SQLITE EXAMPLES
    # =====================================

    sqlite_examples = [

        x for x in dataset

        if x.get(
            "database_type",
            "SQLite"
        ) == "SQLite"
    ]

    print(
        f"SQLite examples available: "
        f"{len(sqlite_examples)}"
    )

    # =====================================
    # SAMPLE SQLITE EXAMPLES
    # =====================================

    sample_size = min(
        POSTGRES_SAMPLES,
        MYSQL_SAMPLES,
        len(sqlite_examples)
    )

    sampled = random.sample(
        sqlite_examples,
        sample_size
    )

    # =====================================
    # CREATE POSTGRESQL COPIES
    # =====================================

    postgres_count = 0

    for example in sampled:

        copied = example.copy()

        copied["database_type"] = "PostgreSQL"

        copied["prompt"] = (
            copied["prompt"]
            .replace(
                "### DATABASE TYPE:\nSQLite",
                "### DATABASE TYPE:\nPostgreSQL"
            )
        )

        final_dataset.append(
            copied
        )

        postgres_count += 1

    # =====================================
    # CREATE MYSQL COPIES
    # =====================================

    mysql_count = 0

    for example in sampled:

        copied = example.copy()

        copied["database_type"] = "MySQL"

        copied["prompt"] = (
            copied["prompt"]
            .replace(
                "### DATABASE TYPE:\nSQLite",
                "### DATABASE TYPE:\nMySQL"
            )
        )

        final_dataset.append(
            copied
        )

        mysql_count += 1

    # =====================================
    # SAVE
    # =====================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_dataset,
            f,
            indent=2
        )

    print("\n" + "=" * 50)

    print(
        f"Original dataset: {len(dataset)}"
    )

    print(
        f"PostgreSQL copies: {postgres_count}"
    )

    print(
        f"MySQL copies: {mysql_count}"
    )

    print(
        f"Final dataset: {len(final_dataset)}"
    )

    print("=" * 50)

    print(
        f"\nSaved -> {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    main()