import ollama2
from db2 import get_schema_representation, execute_sql_query

MODEL = "qwen2.5:7b"


def chat_with_db(user_question: str) -> str:
    # 1. Get database schema
    schema = get_schema_representation()

    # 2. Ask AI to generate SQL
    sql_prompt = f"""
You are a MySQL expert.

Database Schema:
{schema}

User Question:
{user_question}

Create ONE valid MySQL query to answer the question.
Return ONLY raw SQL.
Do NOT use markdown.
Do NOT explain anything.
"""

    response_sql = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": sql_prompt}]
    )

    sql_query = response_sql["message"]["content"]
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    print(f"DEBUG SQL: {sql_query}")

    # 3. Execute SQL
    db_data = execute_sql_query(sql_query)

    # 4. Ask AI to summarize result
    final_prompt = f"""
User Question:
{user_question}

Database Result:
{db_data}

Answer the user clearly in plain language.
"""

    final_response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": final_prompt}]
    )

    return final_response["message"]["content"]
