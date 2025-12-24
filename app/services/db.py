import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="nne"
    )

def fetch_relevant_data(keyword: str) -> str:
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
            SELECT
                bike.id   AS id,
                model.name AS model_name,
                bike.bbshell AS bbshell,
                po.poNo     AS po_no
            FROM nne.bike
            INNER JOIN po    ON po.id = bike.PO
            INNER JOIN model ON model.id = po.model
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
