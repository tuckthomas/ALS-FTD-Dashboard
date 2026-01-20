import psycopg2
import os

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="als_data",
        user="gemini_ai_agent",
        password="gemini_agent_password"
    )
    print("Connection with gemini_ai_agent successful!")
    cur = conn.cursor()
    cur.execute("SELECT usename FROM pg_catalog.pg_user WHERE usename = 'gemini_ai_agent';")
    user = cur.fetchone()
    if user:
        print(f"User {user[0]} exists.")
    else:
        print("User gemini_ai_agent does not exist.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
