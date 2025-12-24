import ollama
from app.services.db import get_database_schema, execute_sql_query

MODEL = "qwen2.5:0.5b"

def chat_with_db(user_question: str) -> str:
    # 1. Get database schema
    schema = get_database_schema()

    # 2. Ask AI to generate SQL
    # Few-Shot Prompt for Tiny Model
    # 0.5B models need examples, they ignore instructions.
    sql_prompt = f"""
You are a MySQL Query Generator.
Schema:
{schema}

Examples:
Q: List all clients
SQL: SELECT * FROM client;

Q: Show me the first 5 clients
SQL: SELECT * FROM client LIMIT 5;

Q: What are the bike models?
SQL: SELECT name FROM model;

Q: How many bikes are there?
SQL: SELECT count(*) FROM bike;

Task:
Q: {user_question}
SQL: 
"""

    try:
        # Log prompt
        with open("sql_debug.log", "a") as f:
            f.write(f"\n--- NEW REQUEST ---\nQ: {user_question}\n")

        response_sql = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": sql_prompt}]
        )
        print(response_sql)
        sql_query = response_sql["message"]["content"]
        print("Generated SQL:", sql_query)
        # Clean the output
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Log generated SQL
        with open("sql_debug.log", "a") as f:
            f.write(f"SQL: {sql_query}\n")
        print(f"Generated SQL: {sql_query}") 

        # 3. Execute SQL
        test_query = "SELECT clientName FROM client;"
        db_data = execute_sql_query(test_query)
        print("DB Data:", db_data)
        # Log DB Result
        with open("sql_debug.log", "a") as f:
            f.write(f"DB Result: {db_data}\n")
        
        # 4. Ask AI to summarize result
        final_prompt = f"""
Data: {db_data}
Question: {user_question}
Answer the question using the Data. If the data is an empty list, say "No results found".
"""
        final_response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": final_prompt}]
        )
        
        return final_response["message"]["content"]

    except Exception as e:
        with open("sql_debug.log", "a") as f:
            f.write(f"ERROR: {e}\n")
        return f"Error processing your request: {str(e)}"
