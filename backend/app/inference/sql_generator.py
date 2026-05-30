from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

import torch


MODEL_NAME = "Qwen/Qwen2.5-Coder-3B-Instruct"


class SQLGenerator:

    def __init__(self):

        print("Loading model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            dtype=torch.float16,
            device_map="auto"
        )

        print("Model loaded successfully!")

    def build_prompt(self, schema: str, question: str):

        prompt = f"""
You are an expert SQL generator.

Generate ONLY a valid SQL query.

Database Schema:
{schema}

Question:
{question}

SQL Query:
"""

        return prompt

    def generate_sql(self, schema: str, question: str):

        prompt = self.build_prompt(
            schema,
            question
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        )

        inputs = {
            k: v.to("cuda")
            for k, v in inputs.items()
        }

        with torch.no_grad():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=True,
                temperature=0.1,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(
           outputs[0],
           skip_special_tokens=True
       )

        sql = generated_text.split("SQL Query:")[-1].strip()

        return sql