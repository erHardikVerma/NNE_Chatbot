import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",      # XAMPP default (confirm if different)
    database="nne"
)

print("CONNECTED OK")

conn.close()
