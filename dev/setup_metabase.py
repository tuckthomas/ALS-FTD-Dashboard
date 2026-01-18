import os
import time
import requests
import json
from dotenv import load_dotenv

# Load env variables including Metabase URL and Admin creds
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

METABASE_URL = "http://localhost:3000"  # Script runs internally/locally
ADMIN_EMAIL = os.getenv("METABASE_ADMIN_EMAIL", "admin@f-als.com")
ADMIN_PASSWORD = os.getenv("METABASE_ADMIN_PASSWORD", "admin")
DB_NAME = os.getenv("POSTGRES_DB", "als_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "admin")
DB_HOST = "db" # internal docker host for Metabase to connect to

def wait_for_metabase():
    print(f"Waiting for Metabase at {METABASE_URL}...")
    for i in range(30):
        try:
            res = requests.get(f"{METABASE_URL}/api/health", timeout=5)
            if res.status_code == 200:
                print("Metabase is healthy!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(5)
        print(f"Waiting... ({i*5}s)")
    return False

def setup_metabase():
    session = requests.Session()

    # 1. Check if setup is needed
    try:
        # Get Setup Token
        res = session.get(f"{METABASE_URL}/api/session/properties")
        props = res.json()
        setup_token = props.get("setup-token")

        if not setup_token:
            print("Metabase already set up or no setup token found.")
            return

        print(f"Found setup token: {setup_token}")

        # 2. Perform Setup
        payload = {
            "token": setup_token,
            "user": {
                "first_name": "Admin",
                "last_name": "User",
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            },
            "prefs": {
                "site_name": "ALS/FTD Research Hub",
                "site_locale": "en",
                "allow_tracking": False
            },
            "database": {
                "engine": "postgres",
                "name": "ALS Data",
                "details": {
                    "host": DB_HOST,
                    "port": 5432,
                    "dbname": DB_NAME,
                    "user": DB_USER,
                    "password": DB_PASS,
                    "db": "postgres" # Metabase internal param?
                }
            }
        }
        
        setup_res = session.post(f"{METABASE_URL}/api/setup", json=payload)
        if setup_res.status_code == 200:
            print("Metabase setup successful!")
            print(f"Admin User: {ADMIN_EMAIL}")
        else:
            print(f"Setup failed: {setup_res.text}")

    except Exception as e:
        print(f"Error during Metabase setup: {e}")

if __name__ == "__main__":
    if wait_for_metabase():
        setup_metabase()
    else:
        print("Could not connect to Metabase.")
