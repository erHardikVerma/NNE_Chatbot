import ollama
from app.services.db import fetch_relevant_data

MODEL = "qwen2.5:7b"

def chat_with_db(prompt: str) -> str:
    try:
        db_context = fetch_relevant_data(prompt)
    except Exception as e:
        # DB failed → continue without DB
        db_context = ""

    if db_context:
        full_prompt = f"""
Use the following database information to answer.

Database data:
{db_context}

User question:
{prompt}
"""
    else:
        full_prompt = prompt

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response["message"]["content"]
