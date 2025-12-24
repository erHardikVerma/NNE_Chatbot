import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="", # XAMPP default
        database="nne"
    )
    cursor = conn.cursor()
    
    print("Tables in database 'nne':")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        print(f"\n--- {table_name} ---")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
            
    conn.close()
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
