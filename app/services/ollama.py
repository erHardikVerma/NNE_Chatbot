import ollama
import os
from app.services.db import get_database_schema, execute_sql_query

MODEL = "qwen2.5:0.5b"
LEARNED_FILE = "learned_examples.txt"

# Simple in-memory session state
SESSION_STATE = {
    "last_question": None,
    "last_sql": None,
    "last_data": None
}

def load_learned_examples():
    """Reads previously confirmed correct examples from file."""
    if not os.path.exists(LEARNED_FILE):
        return ""
    with open(LEARNED_FILE, "r") as f:
        return f.read()

def save_learned_example(question, sql):
    """Saves a confirmed correct example."""
    with open(LEARNED_FILE, "a") as f:
        f.write(f"\nQ: {question}\nSQL: {sql}\n")

def chat_with_db(user_input: str) -> str:
    schema = get_database_schema()
    user_input_lower = user_input.lower().strip()

    # --- 1. HANDLE FEEDBACK ---
    # Strict matching for 1/0 or yes/no
    is_no = user_input_lower in ["no", "0", "n"]
    is_yes = user_input_lower in ["yes", "1", "y"]

    if is_no:
        if not SESSION_STATE["last_question"]:
            return "I don't have a previous query to correct. What can I find for you?"
        
        # Confirmation message
        prefix = "Okay, I'll try again based on your feedback...\n\n"
        
        # Tell AI to try again with different logic
        reprompt = f"""
The user said the previous SQL was WRONG.
Question: {SESSION_STATE['last_question']}
Previous SQL: {SESSION_STATE['last_sql']}
Feedback: This query did not give the expected result. 
Task: Write a DIFFERENT and BETTER MySQL query to answer the question.
Schema: {schema}
Return ONLY the SQL.
"""
        return prefix + perform_sql_task(SESSION_STATE['last_question'], reprompt, is_retry=True)

    if is_yes:
        if SESSION_STATE["last_question"] and SESSION_STATE["last_sql"]:
            save_learned_example(SESSION_STATE["last_question"], SESSION_STATE["last_sql"])
            SESSION_STATE["last_question"] = None # Reset
            return "Great! Feedback saved. What's your next question?"
        return "Glad you're happy! How else can I help?"

    # --- 2. REGULAR CHAT ---
    learned_context = load_learned_examples()
    sql_prompt = f"""
You are a MySQL Query Generator.
Schema:
{schema}

Guidelines:
- ALWAYS use LIMIT (e.g., LIMIT 10) unless asked for "all" or a specific count.
- Select only 2-3 important columns (e.g., name, id) instead of *.

Examples:
{learned_context}
Q: list clients
SQL: SELECT clientName FROM client LIMIT 10;

Q: show the bikes
SQL: SELECT name FROM model LIMIT 5;

Task:
Q: {user_input}
SQL: 
"""
    return perform_sql_task(user_input, sql_prompt)

def perform_sql_task(user_question, prompt, is_retry=False):
    """Helper to generate and execute SQL."""
    try:
        response_sql = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        sql_query = response_sql["message"]["content"].replace("```sql", "").replace("```", "").strip()
        
        # Log for debugging
        with open("sql_debug.log", "a") as f:
            f.write(f"\n[{'RETRY' if is_retry else 'NEW'}] Q: {user_question}\nSQL: {sql_query}\n")

        # Execute
        db_data = execute_sql_query(sql_query)
        
        # Update Session State
        SESSION_STATE["last_question"] = user_question
        SESSION_STATE["last_sql"] = sql_query
        SESSION_STATE["last_data"] = db_data

        result_msg = f"Results from Database:\n{db_data}"
        feedback_prompt = "\n\n--- Was this result correct? (Yes/No) ---"
        
        return result_msg + feedback_prompt

    except Exception as e:
        return f"System Error during {'retry' if is_retry else 'query'}: {str(e)}"
