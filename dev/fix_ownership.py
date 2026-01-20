import psycopg2
import os

def fix():
    try:
        print("Connecting to DB...")
        conn = psycopg2.connect(
            dbname="als_data",
            user="postgres",
            password="root_password",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Grant permissions
        print("Granting ownership to gemini_ai_agent...")
        cur.execute("ALTER TABLE \"Dashboard_intervention\" OWNER TO gemini_ai_agent;")
        print("Success.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix()
