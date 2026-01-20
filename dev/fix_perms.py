import psycopg2
import os

# Connect as superuser
conn = psycopg2.connect(
    dbname="als_data",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cur = conn.cursor()

try:
    print("Granting permissions...")
    cur.execute("GRANT ALL ON SCHEMA public TO gemini_ai_agent;")
    cur.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gemini_ai_agent;")
    cur.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gemini_ai_agent;")
    print("Permissions granted successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close()
