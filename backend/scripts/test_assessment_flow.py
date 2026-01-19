"""
Test Assessment Flow
====================
Verifies the end-to-end flow of the new Assessment API.
1. Authenticates as a patient.
2. Starts a new session.
3. Sends a chat message.
4. Checks history.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# Reuse the verify_auth_v2 logic to get a token
def get_patient_token():
    print("\n🔹 Authenticating...")
    # Register a temp user
    import random
    suffix = random.randint(10000, 99999)
    email = f"assessment_test_{suffix}@example.com"
    password = "TestPassword123!"
    
    reg_url = f"{BASE_URL}/auth/register"
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Assessment",
        "last_name": "Tester",
        "user_type": "patient"
    }
    
    try:
        resp = requests.post(reg_url, params=reg_payload)
        if resp.status_code == 200:
            print(f"✅ Registered: {email}")
            return resp.json()["access_token"]
        else:
            print(f"❌ Registration failed: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

def test_start_session(token):
    print("\n🔹 Starting Session...")
    url = f"{BASE_URL}/assessment/start"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.post(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Session Started: {data['session_id']}")
            print(f"   Greeting: {data['greeting']}")
            return data["session_id"]
        else:
            print(f"❌ Start Session Failed: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Start Error: {e}")
        return None

def test_chat(token, session_id):
    print("\n🔹 Sending Chat Message...")
    url = f"{BASE_URL}/assessment/chat"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "message": "I've been feeling really anxious about my job lately.",
        "session_id": session_id
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Chat Response Received")
            print(f"   Response: {data['response']}")
            return True
        else:
            print(f"❌ Chat Failed: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return False

def test_history(token, session_id):
    print("\n🔹 Checking History...")
    url = f"{BASE_URL}/assessment/history/{session_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            msg_count = data["total_messages"]
            print(f"✅ History Retrieved: {msg_count} messages")
            for msg in data["messages"]:
                print(f"   [{msg['role']}]: {msg['content'][:50]}...")
            return True
        else:
            print(f"❌ History Failed: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ History Error: {e}")
        return False

if __name__ == "__main__":
    token = get_patient_token()
    if token:
        session_id = test_start_session(token)
        if session_id:
            test_chat(token, session_id)
            test_history(token, session_id)
