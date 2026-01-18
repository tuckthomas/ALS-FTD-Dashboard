import os
import requests
import json
from dotenv import load_dotenv

# Load env variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

METABASE_URL = "http://192.168.0.101:3000" # Use user's IP as configured
ADMIN_EMAIL = os.getenv("METABASE_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("METABASE_ADMIN_PASSWORD")

def check_dashboards():
    session = requests.Session()
    
    # Login
    try:
        login_payload = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        res = session.post(f"{METABASE_URL}/api/session", json=login_payload)
        if res.status_code != 200:
            print(f"Login failed: {res.status_code} - {res.text}")
            return
            
        print("Logged in successfully.")
        
        # List Dashboards
        res = session.get(f"{METABASE_URL}/api/dashboard")
        if res.status_code == 200:
            dashboards = res.json()
            print(f"Found {len(dashboards)} dashboards:")
            for d in dashboards:
                print(f" - ID: {d['id']}, Name: '{d['name']}', Public UUID: {d.get('public_uuid')}, Enable Embedding: {d.get('enable_embedding')}")
        else:
             print(f"Failed to list dashboards: {res.status_code}")

    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_dashboards()
