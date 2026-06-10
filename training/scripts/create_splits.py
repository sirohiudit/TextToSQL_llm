import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR = BASE_DIR / "data" / "processed"


RANDOM_SEED = 42

TRAIN_RATIO = 0.9
VAL_RATIO = 0.1


# ==========================================
# LOAD DATASET
# ==========================================

dataset_path = PROCESSED_DIR / "final_multidialect_dataset.json"

with open(dataset_path, "r", encoding="utf-8") as f:

    dataset = json.load(f)

print(f"\nLoaded {len(dataset)} examples")


# ==========================================
# SHUFFLE
# ==========================================

random.seed(RANDOM_SEED)

random.shuffle(dataset)


# ==========================================
# SPLIT
# ==========================================

train_size = int(
    len(dataset) * TRAIN_RATIO
)

train_dataset = dataset[:train_size]

val_dataset = dataset[train_size:]


# ==========================================
# SAVE
# ==========================================

train_path = OUTPUT_DIR / "train_dataset.json"

val_path = OUTPUT_DIR / "val_dataset.json"


with open(train_path, "w", encoding="utf-8") as f:

    json.dump(train_dataset, f, indent=2)


with open(val_path, "w", encoding="utf-8") as f:

    json.dump(val_dataset, f, indent=2)


# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 50)

print(f"Train samples: {len(train_dataset)}")

print(f"Validation samples: {len(val_dataset)}")

print("=" * 50)

print("\nSaved train/validation splits")