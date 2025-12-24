import ollama
<<<<<<< HEAD
from app.services.db import fetch_relevant_data
=======
from app.services.db import get_database_schema, execute_sql_query
>>>>>>> e93679e (v2: Switched to lightweight Qwen-0.5b with Few-Shot prompting and dynamic schema extraction)

MODEL = "qwen2.5:0.5b"

<<<<<<< HEAD
def chat_with_db(prompt: str) -> str:
    try:
        db_context = fetch_relevant_data(prompt)
    except Exception as e:
        # DB failed → continue without DB
        db_context = ""

    if db_context:
        full_prompt = f"""
Use the following database information to answer.
=======
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
>>>>>>> e93679e (v2: Switched to lightweight Qwen-0.5b with Few-Shot prompting and dynamic schema extraction)

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
    else:
        full_prompt = prompt

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
        db_data = execute_sql_query(sql_query)
        
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
