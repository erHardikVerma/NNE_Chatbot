import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="nne"
    )


def get_schema_representation() -> str:
    """
    Text description of database schema.
    Update this when tables/columns change.
    """
    return """
Table: bike
Columns:
- id (INT)
- bbshell (TEXT)
- PO (INT, foreign key -> po.id)

Table: po
Columns:
- id (INT)
- poNo (TEXT)
- model (INT, foreign key -> model.id)

Table: model
Columns:
- id (INT)
- name (TEXT)
"""


def execute_sql_query(query: str) -> str:
    """
    Executes a raw SQL query.
    ⚠️ Use ONLY for internal / controlled queries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return str(result)

    except Exception as e:
        return f"SQL Error: {e}"

    finally:
        cursor.close()
        conn.close()
