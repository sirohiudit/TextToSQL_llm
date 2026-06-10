from datasets import load_dataset

from unsloth import FastLanguageModel

from transformers import TrainingArguments

from trl.trainer.sft_trainer import SFTTrainer


# ==========================================
# CONFIG
# ==========================================

MODEL_NAME = "Qwen/Qwen2.5-Coder-3B-Instruct"

MAX_SEQ_LENGTH = 2048

OUTPUT_DIR = "training/outputs/qwen_sql_model_v2"


# ==========================================
# LOAD MODEL
# ==========================================

print("\nLoading model...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

print("\nApplying LoRA...")

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)


# ==========================================
# LOAD DATASET
# ==========================================

print("\nLoading dataset...")

dataset = load_dataset(
    "json",
    data_files={
        "train": "training/data/processed/train_dataset.json",
        "validation": "training/data/processed/val_dataset.json"
    }
)

print(dataset)


# ==========================================
# FORMAT DATA
# ==========================================

def formatting_func(example):

    text = (
        example["prompt"]
        + example["response"]
        + tokenizer.eos_token
    )

    return {
        "text": text
    }


dataset = dataset.map(
    formatting_func
)


# ==========================================
# TRAINER
# ==========================================

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,
    args=TrainingArguments(
        output_dir=OUTPUT_DIR,

        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,

        warmup_ratio=0.03,

        num_train_epochs=1,

        learning_rate=1e-4,

        fp16=False,
        bf16=True,

        logging_steps=10,

        eval_strategy="steps",
        eval_steps=2000,

        save_strategy="steps",
        save_steps=2000,

        optim="adamw_torch",

        weight_decay=0.01,

        lr_scheduler_type="cosine",

        seed=42,
    ),
)


# ==========================================
# TRAIN
# ==========================================

print("\nStarting training...")

trainer.train()


# ==========================================
# SAVE MODEL
# ==========================================

print("\nSaving model...")

trainer.save_model(
    OUTPUT_DIR
)

tokenizer.save_pretrained(
    OUTPUT_DIR
)

print("\nTraining complete!")

