import requests
import os
import json

METABASE_URL = "http://localhost:3000"
SESSION_ID = "80d5e94a-2926-4272-aab5-f6bf60c7219d" # From previous turn, or re-auth if needed
DB_ID = 2

def get_session():
    # Try to auth just in case session expired
    try:
        resp = requests.post(f"{METABASE_URL}/api/session", json={
            "username": "tuckerolson13@gmail.com",
            "password": "RbnIO#$tr133"
        })
        if resp.status_code == 200:
            return resp.json()['id']
    except:
        pass
    return SESSION_ID

def hide_tables():
    session_id = get_session()
    headers = {"X-Metabase-Session": session_id, "Content-Type": "application/json"}
    
    # 1. Get all tables for the database
    # We need to hit /api/database/:id/metadata to get the table list with IDs
    print("Fetching tables...")
    resp = requests.get(f"{METABASE_URL}/api/database/{DB_ID}/metadata", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch metadata: {resp.text}")
        return

    data = resp.json()
    tables = data.get('tables', [])
    
    print(f"Found {len(tables)} tables.")
    
    # 2. Iterate and hide unwanted tables
    # We want to keep tables starting with "Dashboard_"
    # We might also want separate lists if there are specific ones to keep
    
    count_hidden = 0
    for table in tables:
        t_name = table['name']
        t_id = table['id']
        t_schema = table['schema']
        
        # Logic: If it's in 'public' schema AND does NOT start with 'Dashboard_', hide it.
        # We also keep 'Dashboard_' tables visible.
        
        if not t_name.startswith("Dashboard_"):
            # Hide it
            print(f"Hiding table: {t_name} (ID: {t_id})")
            
            # The API to update a table is PUT /api/table/:id
            # visibility_type: "hidden" 
            update_payload = {"visibility_type": "hidden"}
            
            r = requests.put(f"{METABASE_URL}/api/table/{t_id}", headers=headers, json=update_payload)
            if r.status_code == 200:
                count_hidden += 1
            else:
                print(f"Failed to hide {t_name}: {r.status_code} - {r.text}")
        else:
            print(f"Keeping visible: {t_name}")
            # Ensure it is visible (in case it was hidden before?)
            # requests.put(f"{METABASE_URL}/api/table/{t_id}", headers=headers, json={"visibility_type": None})

    print(f"Operation complete. Hidden {count_hidden} tables.")

if __name__ == "__main__":
    hide_tables()
