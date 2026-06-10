import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR = BASE_DIR / "data" / "processed"


MAX_PROMPT_LENGTH = 10000
MAX_RESPONSE_LENGTH = 1000


# ==========================================
# LOAD DATASET
# ==========================================

dataset_path = PROCESSED_DIR / "final_dataset.json"

with open(dataset_path, "r", encoding="utf-8") as f:

    dataset = json.load(f)

print(f"\nLoaded {len(dataset)} examples")


# ==========================================
# CLEANING
# ==========================================

cleaned = []

seen = set()

removed_duplicates = 0
removed_invalid = 0
removed_long = 0


for example in dataset:

    prompt = example.get("prompt", "").strip()

    response = example.get("response", "").strip()

    # ==========================
    # EMPTY CHECK
    # ==========================

    if not prompt or not response:

        removed_invalid += 1
        continue

    # ==========================
    # SQL VALIDITY CHECK
    # ==========================

    response_upper = response.upper()

    valid_sql = any([
        response_upper.startswith("SELECT"),
        response_upper.startswith("WITH")
    ])

    if not valid_sql:

        removed_invalid += 1
        continue

    # ==========================
    # LENGTH CHECK
    # ==========================

    if len(prompt) > MAX_PROMPT_LENGTH:

        removed_long += 1
        continue

    if len(response) > MAX_RESPONSE_LENGTH:

        removed_long += 1
        continue

    # ==========================
    # DUPLICATE CHECK
    # ==========================

    key = (prompt, response)

    if key in seen:

        removed_duplicates += 1
        continue

    seen.add(key)

    # ==========================
    # NORMALIZATION
    # ==========================

    response = response.replace("\n", " ")

    response = " ".join(response.split())

    cleaned.append({
        "database_type": example.get("database_type", "SQLite"),
        "prompt": prompt,
        "response": response
    })


# ==========================================
# SAVE CLEAN DATASET
# ==========================================

output_path = OUTPUT_DIR / "cleaned_dataset.json"

with open(output_path, "w", encoding="utf-8") as f:

    json.dump(cleaned, f, indent=2)

print("\n" + "=" * 50)

print(f"Original examples: {len(dataset)}")

print(f"Cleaned examples: {len(cleaned)}")

print(f"Removed duplicates: {removed_duplicates}")

print(f"Removed invalid: {removed_invalid}")

print(f"Removed long samples: {removed_long}")

print("=" * 50)

print("\nSaved cleaned dataset")