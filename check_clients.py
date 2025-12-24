import mysql.connector

def check_clients():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="nne"
        )
        cursor = conn.cursor()
        
        print("Connected to database 'nne'...")
        
        # Query the client table
        cursor.execute("SELECT * FROM client LIMIT 5")
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} clients (showing first 5):")
        for row in rows:
            print(row)
            
        conn.close()
        print("✅ Connection Successful")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    check_clients()
