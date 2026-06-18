class QueryRepair:

    @staticmethod
    def build_prompt(
        question,
        failed_sql,
        error_message,
        schema,
        database_type="SQLite",
        conversation_history=None
    ):
        
        history_text = ""

        if conversation_history:

            for items in conversation_history[-3:]:

                history_text += f"""

Previous Question:
{items['question']}

Previous SQL:
{items['generated_sql']}"""
                
        return f"""

You are an expert SQL repair system.

Your task is to repair a failed SQL query.

STRICT RULES:
1. Return ONLY SQL
2. No markdown
3. No explanation
4. Keep original intent
5. Use only schema columns/tables
6. Preserve filters whenever possible
7. Preserve aggregations whenever possible
8. Preserve joins whenever possible
9. Output valid {database_type} SQL

Database Type:
{database_type}

Database Schema:
{schema}

Conversation Context:
{history_text}

Original Question:
{question}

Failed SQL:
{failed_sql}

Database Error:
{error_message}

Correct SQL:
"""