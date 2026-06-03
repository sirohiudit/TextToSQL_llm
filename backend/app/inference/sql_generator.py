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

    def build_prompt(self, schema: str, question: str, conversation_history=None):
        conversation_context = ""

        if conversation_history:

         for item in conversation_history[-3:]:

             conversation_context += f"""

        Previous Question:
        {item['question']}

        Previous SQL:
        {item['sql']}
       """

        prompt = f"""
You are an expert SQLite SQL generator.

Your task is to generate ONLY valid SQLite SQL queries.

STRICT RULES:
1. Output ONLY SQL
2. Do NOT explain anything
3. Do NOT use markdown
4. Do NOT generate multiple queries
5. Use only tables and columns from schema
6. Prefer explicit JOINs
7. Use proper aggregation when needed
8. Generate syntactically correct SQLite SQL

Database Schema:
{schema}

Question:
{question}

SQL Query:
"""

        return prompt

    def generate_sql(self, schema: str, question: str, conversation_history=None):

        prompt = self.build_prompt(
            schema,
            question,
            conversation_history
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

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

        generated_text = self.tokenizer.decode(
           generated_tokens,
           skip_special_tokens=True
      )  

# Remove markdown blocks
        generated_text = generated_text.replace("```sql", "")
        generated_text = generated_text.replace("```", "")

        generated_text = generated_text.strip()

# Keep only first SQL statement
        if ";" in generated_text:
          sql = generated_text.split(";")[0] + ";"
        else:
          sql = generated_text

        return sql.strip()