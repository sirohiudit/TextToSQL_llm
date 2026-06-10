from unsloth import FastLanguageModel
import torch

MODEL_PATH = "training/outputs/qwen_sql_model_v2"


class SQLGenerator:

    def __init__(self):

        print("Loading v2 model...")

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
         model_name=MODEL_PATH,
         max_seq_length=2048,
         dtype=None,
         load_in_4bit=True,
        )

        FastLanguageModel.for_inference(self.model)

        print("V2 model loaded successfully!")

    def build_prompt(self, schema: str, question: str, database_type: str, conversation_history=None):
        conversation_context = ""

        if conversation_history:
            for item in conversation_history[-3:]:
                conversation_context += f"""

        Previous Question:
        {item['question']}

        Previous SQL:
        {item['sql']}
       """

        # ====================================
        # DIALECT RULES
        # ====================================
        if database_type == "SQLite":
            dialect_rules = """
             - Use SQLite syntax only
             - Use strftime() for date formatting
             - Do NOT use date_trunc()
             - Do NOT use DATE_FORMAT()
            """

        elif database_type == "PostgreSQL":
             dialect_rules = """
                 - Use PostgreSQL syntax only
                 - Use date_trunc() for date aggregation
                 - Do NOT use strftime()
                 - Do NOT use DATE_FORMAT()
                """
        elif database_type == "MySQL":
              dialect_rules = """
                 - Use MySQL syntax only
                 - Use DATE_FORMAT() for date aggregation
                 - Do NOT use date_trunc()
                 - Do NOT use strftime()
                """

        else:
           dialect_rules = """
             - Use standard ANSI SQL
            """    




        prompt = f"""
You are an expert {database_type} SQL generator.

Your task is to generate ONLY valid {database_type} SQL queries.

STRICT RULES:
1. Output ONLY SQL
2. Do NOT explain anything
3. Do NOT use markdown
4. Do NOT generate multiple queries
5. Use only tables and columns from schema
6. Prefer explicit JOINs
7. Use proper aggregation when needed
8. Generate syntactically correct {database_type} SQL

Database Type:
{database_type}

Dialect Rules:
{dialect_rules}

Database Schema:
{schema}

Question:
{question}

SQL Query:
"""

        return prompt

    def generate_sql(self, schema: str, question: str, database_type: str, conversation_history=None):

        prompt = self.build_prompt(
            schema=schema,
            question=question,
            database_type="SQLite",
            conversation_history=conversation_history
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