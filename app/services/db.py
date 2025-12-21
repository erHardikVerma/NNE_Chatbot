import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="your_db"
    )

def fetch_relevant_data(keyword: str) -> str:
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT name, description
    FROM products
    WHERE description LIKE %s
    LIMIT 5
    """
    cur.execute(query, (f"%{keyword}%",))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert rows → text
    context = ""
    for r in rows:
        context += f"Name: {r[0]}, Description: {r[1]}\n"

    return context
