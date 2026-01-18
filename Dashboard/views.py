from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import requests
import os
import json
import uuid

# Superset API Configuration
SUPERSET_URL = os.environ.get("SUPERSET_URL")
ADMIN_USERNAME = os.environ.get("SUPERSET_ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("SUPERSET_ADMIN_PASSWORD")

def get_superset_auth_context():
    """Authenticates and returns session, access_token, csrf_token."""
    session = requests.Session()
    
    # 1. Login
    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "provider": "db",
        "refresh": True
    }
    
    try:
        response = session.post(login_url, json=payload)
        response.raise_for_status()
        access_token = response.json().get('access_token')
        
        # 2. Get CSRF Token
        csrf_url = f"{SUPERSET_URL}/api/v1/security/csrf_token/"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        csrf_response = session.get(csrf_url, headers=headers)
        csrf_response.raise_for_status()
        csrf_token = csrf_response.json().get('result')
        
        return session, access_token, csrf_token
    except Exception as e:
        print(f"Error in Superset auth: {e}")
        return None, None, None

def get_first_dashboard_id(session, access_token):
    """Fetches the first available dashboard ID."""
    dash_url = f"{SUPERSET_URL}/api/v1/dashboard/"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = session.get(dash_url, headers=headers)
        response.raise_for_status()
        dashboards = response.json().get('result', [])
        if dashboards:
            return str(dashboards[0]['id'])
        return None
    except Exception as e:
        print(f"Error listing dashboards: {e}")
        return None

def get_guest_token(session, dashboard_id, access_token, csrf_token):
    """Fetches a guest token for the embedded dashboard."""
    guest_token_url = f"{SUPERSET_URL}/api/v1/security/guest_token/"
    
    payload = {
        "user": {
            "username": "guest_user",
            "first_name": "Guest",
            "last_name": "User"
        },
        "resources": [{"type": "dashboard", "id": str(dashboard_id)}],
        "rls": []
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-CSRFToken": csrf_token,
        "Referer": SUPERSET_URL  # Sometimes needed
    }
    
    try:
        # Important: pass headers here, but session cookies are auto-included
        response = session.post(guest_token_url, json=payload, headers=headers)
        if response.status_code != 200:
             print(f"Failed to get guest token: {response.text}")
             
        response.raise_for_status()
        return response.json().get('token')
    except Exception as e:
        print(f"Error fetching guest token: {e}")
        return None

@api_view(['GET'])
def get_dashboard_token(request):
    """API Endpoint to get a guest token for the frontend."""
    
    # 1. Authenticate (Session + Tokens)
    session, access_token, csrf_token = get_superset_auth_context()
    if not access_token or not csrf_token:
        return Response({"error": "Failed to authenticate with analytics engine"}, status=500)
    
    # 2. Get Dashboard ID (Dynamic)
    dashboard_id = get_first_dashboard_id(session, access_token)
    if not dashboard_id:
        return Response({
            "error": "No dashboards found. Please create one."
        }, status=404)
    
    # 3. Get Guest Token
    guest_token = get_guest_token(session, dashboard_id, access_token, csrf_token)
    
    if not guest_token:
        return Response({"error": f"Failed to generate guest token for dashboard {dashboard_id}"}, status=404)
        
    return Response({
        "token": guest_token,
        "dashboard_id": dashboard_id,
        "superset_domain": os.environ.get("SUPERSET_PUBLIC_URL") 
    })
