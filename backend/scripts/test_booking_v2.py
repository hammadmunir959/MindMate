import requests
import sys
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
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
        # Note: Current auth API expects query params
        r = requests.post(f"{AUTH_URL}/register", params=reg_data)
        if r.status_code not in [200, 400]: # 400 if already exists
             print(f"Register failed: {r.text}")
        
        # Login
        login_data = {
            "username": email,
            "password": password
        }
        # Endpoint is /login/access-token
        response = requests.post(f"{AUTH_URL}/login/access-token", data=login_data)
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def test_booking_flow():
    print("🚀 Starting Booking System Test...")

    # 1. Setup Users
    patient_email = f"patient_{int(datetime.now().timestamp())}@test.com"
    specialist_email = f"spec_{int(datetime.now().timestamp())}@test.com"
    password = "password123"

    print(f"\nCreating users...\nPatient: {patient_email}\nSpecialist: {specialist_email}")

    patient_token = get_token(patient_email, password, "patient")
    spec_token = get_token(specialist_email, password, "specialist")

    if not patient_token or not spec_token:
        print("❌ Failed to authenticate users")
        return

    # Need specialist ID - usually would get from profile, here assuming auth creates profile
    # Use /test-token endpoint to get ID
    spec_headers = {"Authorization": f"Bearer {spec_token}"}
    spec_resp = requests.post(f"{AUTH_URL}/test-token", headers=spec_headers)
    if spec_resp.status_code != 200:
        print(f"❌ Failed to get token info: {spec_resp.status_code} {spec_resp.text}")
        return
    spec_me = spec_resp.json()
    spec_id = spec_me.get("specialist_id")
    
    if not spec_id:
        print("❌ Could not get specialist ID from token endpoint")
        print(f"Debug Spec Me: {json.dumps(spec_me, indent=2)}")
        return

    print(f"Specialist ID: {spec_id}")

    # 2. Get Available Slots (Patient)
    print("\nfetching available slots...")
    headers = {"Authorization": f"Bearer {patient_token}"}
    slots_resp = requests.get(f"{BOOKING_URL}/slots/{spec_id}", headers=headers)
    
    if slots_resp.status_code != 200:
        print(f"❌ Failed to get slots: {slots_resp.text}")
        return

    slots = slots_resp.json()
    print(f"Found {len(slots)} slots")
    if not slots:
        print("❌ No slots available")
        return

    target_slot = slots[0]
    print(f"Booking slot: {target_slot}")

    # 3. Book Appointment (Patient)
    print("\nBooking appointment...")
    booking_data = {
        "specialist_id": spec_id,
        "date": target_slot["date"],
        "time": target_slot["time"],
        "notes": "Testing booking flow"
    }
    book_resp = requests.post(f"{BOOKING_URL}/book", headers=headers, json=booking_data)
    
    if book_resp.status_code != 200:
        print(f"❌ Booking failed: {book_resp.text}")
        return

    appointment = book_resp.json()
    appt_id = appointment["id"]
    print(f"✅ Booking created! ID: {appt_id}, Status: {appointment['status']}")

    # 4. Confirm Appointment (Specialist)
    print("\nConfirming appointment (Specialist)...")
    confirm_resp = requests.post(
        f"{BOOKING_URL}/{appt_id}/confirm", 
        headers=spec_headers
    )
    
    if confirm_resp.status_code != 200:
        print(f"❌ Confirmation failed: {confirm_resp.text}")
        return

    confirmed_appt = confirm_resp.json()
    print(f"✅ Appointment Status: {confirmed_appt['status']}")
    
    if confirmed_appt["status"] == "CONFIRMED":
        print("\n🎉 Booking Flow Verification PASSED!")
    else:
        print("\n❌ Booking status mismatch")

if __name__ == "__main__":
    test_booking_flow()
