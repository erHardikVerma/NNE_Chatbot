from app.services.db import get_database_schema, execute_sql_query
from app.services.ollama import chat_with_db

def test_schema():
    print("--- Testing Schema Extraction ---")
    try:
        schema = get_database_schema()
        # Print first 200 chars to verify
        print(f"Schema Preview: {schema[:200]}...")
        if "Table:" in schema:
            print("[OK] Schema Extraction Success")
        else:
            print("[FAIL] Schema Extraction Failed")
    except Exception as e:
        print(f"[FAIL] Schema Error: {e}")

def test_chat():
    print("\n--- Testing Chat (Text-to-SQL) ---")
    question = "How many clients are there?"
    print(f"Question: {question}")
    
    try:
        response = chat_with_db(question)
        print(f"Response: {response}")
        # We expect a number or a sentence containing a number
        if response:
            print("[OK] Chat Success")
        else:
            print("[FAIL] Chat Failed (Empty response)")
    except Exception as e:
        print(f"[FAIL] Chat Error: {e}")

if __name__ == "__main__":
    test_schema()
    test_chat()
