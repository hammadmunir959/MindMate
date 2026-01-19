"""
Verify Authentication V2
========================
Tests the new unified authentication system (User + Patient/Specialist profiles).
1. Registers a new patient.
2. Logs in to get access token.
3. Verifies token access.
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    print("\n🔹 Testing Registration...")
    url = f"{BASE_URL}/auth/register"
    
    # Randomize email to allow repeated runs
    import random
    suffix = random.randint(1000, 9999)
    email = f"test_patient_{suffix}@example.com"
    password = "SecurePassword123!"
    
    payload = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "Patient",
        "user_type": "patient"
    }
    
    try:
        response = requests.post(url, params=payload) # Using params as the endpoint uses query params currently in signature
        # Wait, the auth_new.py definition:
        # def register(*, db=..., email: str, ...)
        # These are query parameters by default in FastAPI unless Body() is used.
        # Let's try sending as query params first, or JSON body if it was Pydantic (it wasn't).
        
        if response.status_code == 200:
            print(f"✅ Registration Configured: {response.json()}")
            return email, password
        else:
            print(f"❌ Registration Failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_login(email, password):
    print("\n🔹 Testing Login...")
    url = f"{BASE_URL}/auth/login/access-token"
    
    # OAuth2 form data
    data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login Success: Token received")
            return token_data["access_token"]
        else:
            print(f"❌ Login Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_token_access(token):
    print("\n🔹 Testing Token Access...")
    url = f"{BASE_URL}/auth/test-token"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Token Verified: {response.json()}")
            return True
        else:
            print(f"❌ Token Verification Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    email, password = test_registration()
    if email and password:
        token = test_login(email, password)
        if token:
            test_token_access(token)
