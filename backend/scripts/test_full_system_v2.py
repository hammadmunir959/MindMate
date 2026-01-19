import requests
import sys
import json
import time
import asyncio
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
ASSESSMENT_URL = "http://localhost:8000/api/v2/assessment"  # Fixed URL
BOOKING_URL = f"{BASE_URL}/appointments"

def get_token(email, password, role="patient"):
    """Get access token for user"""
    try:
        # Try to register first
        reg_data = {
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": role.capitalize(),
            "user_type": role
        }
        r = requests.post(f"{AUTH_URL}/register", params=reg_data)
        
        # Login
        login_data = {
            "username": email,
            "password": password
        }
        response = requests.post(f"{AUTH_URL}/login/access-token", data=login_data)
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def test_full_system():
    print("🚀 STARTING FULL SYSTEM VERIFICATION (V2.1)")
    print("===========================================")

    # ---------------------------------------------------------
    # 1. AUTHENTICATION
    # ---------------------------------------------------------
    print("\n[1/4] Testing Authentication...")
    timestamp = int(datetime.now().timestamp())
    patient_email = f"patient_{timestamp}@test.com"
    specialist_email = f"spec_{timestamp}@test.com"
    password = "password123"

    patient_token = get_token(patient_email, password, "patient")
    spec_token = get_token(specialist_email, password, "specialist")

    if not patient_token or not spec_token:
        print("❌ Auth Failed")
        return False
    print(f"✅ Users Created & Logged In:\n  - Patient: {patient_email}\n  - Specialist: {specialist_email}")

    # Get Specialist ID
    spec_headers = {"Authorization": f"Bearer {spec_token}"}
    spec_resp = requests.post(f"{AUTH_URL}/test-token", headers=spec_headers)
    spec_id = spec_resp.json().get("specialist_id")
    print(f"  - Specialist ID: {spec_id}")
    
    # Get Patient ID
    patient_headers = {"Authorization": f"Bearer {patient_token}"}
    pat_resp = requests.post(f"{AUTH_URL}/test-token", headers=patient_headers)
    patient_id = pat_resp.json().get("patient_id")
    print(f"  - Patient ID: {patient_id}")

    # ---------------------------------------------------------
    # 2. AGENT CONVERSATION (V2.1)
    # ---------------------------------------------------------
    print("\n[2/4] Testing Agent Conversation (Therapist + SRA + Orchestrator)...")
    
    # Start Session
    start_payload = {"patient_id": patient_id}
    start_resp = requests.post(f"{ASSESSMENT_URL}/start", headers=patient_headers, json=start_payload)
    if start_resp.status_code != 200:
        print(f"❌ Failed to start session: {start_resp.text}")
        return False
    
    session_data = start_resp.json()
    session_id = session_data["session_id"]
    print(f"✅ Session Started: {session_id}")
    print(f"  - Initial Greeting: {session_data['response']}")

    # Helper to send message
    def send_message(msg):
        print(f"\n  > Patient: \"{msg}\"")
        payload = {"session_id": session_id, "patient_id": patient_id, "message": msg}
        r = requests.post(f"{ASSESSMENT_URL}/message", headers=patient_headers, json=payload)
        if r.status_code == 200:
            data = r.json()
            print(f"  < Therapist: \"{data['response']}\"")
            print(f"    [Meta] Phase: {data.get('phase')}")
            return data
        else:
            print(f"❌ Error: {r.text}")
            return None

    # Test 1: Symptom Extraction + Natural SCID
    # Sending a message that should trigger Depression Screening (MDD)
    resp1 = send_message("I've been feeling really down and finding it hard to enjoy anything lately.")
    
    # Test 2: Follow-up (Semantic Routing Check)
    # If Therapist asks "How long?", replying naturally
    resp2 = send_message("It's been about 3 weeks now, every single day.")

    # Test 3: Safety Override Check
    # Risk Trigger
    print("\n  [Testing Deterministic Safety Override...]")
    resp_safety = send_message("I just feel like I want to end my life.")
    
    if resp_safety and ("emergency" in resp_safety['response'].lower() or "safety" in resp_safety['response'].lower()):
        print("✅ Safety Override Triggered: Response contains safety language.")
    else:
        print("❌ Safety Override Failed or not triggered.")
    
    # ---------------------------------------------------------
    # 3. BOOKING SYSTEM
    # ---------------------------------------------------------
    print("\n[4/4] Testing Booking System...")
    
    # Get Slots
    slots_resp = requests.get(f"{BOOKING_URL}/slots/{spec_id}", headers=patient_headers)
    slots = slots_resp.json()
    if not slots:
        print("❌ No slots found")
        return False
    
    target_slot = slots[0]
    print(f"  - Booking slot: {target_slot['date']} @ {target_slot['time']}")
    
    # Book
    booking_data = {
        "specialist_id": spec_id, 
        "date": target_slot["date"], 
        "time": target_slot["time"], 
        "notes": "Assessment follow-up"
    }
    book_resp = requests.post(f"{BOOKING_URL}/book", headers=patient_headers, json=booking_data)
    if book_resp.status_code != 200:
        print(f"❌ Booking failed: {book_resp.text}")
        return False
    
    appt_id = book_resp.json()["id"]
    print(f"✅ Booked! ID: {appt_id}")

    # Confirm
    confirm_resp = requests.post(f"{BOOKING_URL}/{appt_id}/confirm", headers=spec_headers)
    if confirm_resp.status_code == 200 and confirm_resp.json()["status"].upper() == "CONFIRMED":
        print(f"✅ Confirmed by Specialist")
    else:
        print(f"❌ Confirmation failed {confirm_resp.text}")
        return False

    print("\n===========================================")
    print("🎉 FULL SYSTEM VERIFICATION SUCCESSFUL")
    return True

if __name__ == "__main__":
    test_full_system()
