from app.services.db import fetch_relevant_data
import ollama

MODEL = "qwen2.5:7b"

def chat_with_db(prompt: str):
    db_context = fetch_relevant_data(prompt)

    full_prompt = f"""
Use the following database information to answer.

Database data:
{db_context}

User question:
{prompt}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response["message"]["content"]
