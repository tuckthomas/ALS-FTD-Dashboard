import psycopg2
def fix():
    try:
        conn = psycopg2.connect(dbname="als_data", user="postgres", password="root_password", host="localhost", port="5432")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("ALTER SEQUENCE \"Dashboard_intervention_id_seq\" OWNER TO gemini_ai_agent;")
        conn.close()
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    fix()

