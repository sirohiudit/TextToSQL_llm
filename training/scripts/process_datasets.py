import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print("Loading WikiSQL...")

    wikisql = load_json(
        PROCESSED_DIR / "wikisql_processed.json"
    )

    print("Loading Spider...")

    spider = load_json(
        PROCESSED_DIR / "spider_processed.json"
    )

    print("Loading BIRD...")

    bird = load_json(
      PROCESSED_DIR / "bird_processed.json"
    )

    combined = []

    for example in wikisql + spider + bird:
        if "database_type" not in example:
            example["database_type"] = "SQLite"
            
        combined.append(example)    

    print(f"\nTotal examples: {len(combined)}")

    output_path = PROCESSED_DIR / "final_dataset.json"

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(combined, f, indent=2)

    print("\nSaved final dataset")


if __name__ == "__main__":

    main()