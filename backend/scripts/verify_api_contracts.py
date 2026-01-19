import requests
import sys
import uuid
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
EMAIL = f"test_patient_{uuid.uuid4().hex[:8]}@example.com"
PASSWORD = "TestPassword123!"
FIRST_NAME = "Test"
LAST_NAME = "Patient"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log(message, status="INFO"):
    if status == "PASS":
        print(f"{Colors.GREEN}[PASS] {message}{Colors.RESET}")
    elif status == "FAIL":
        print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")
    else:
        print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")

def test_auth():
    log("=== Testing Authentication Endpoints ===")
    
    # 1. Register
    log(f"Registering user: {EMAIL}...")
    try:
        resp = requests.post(f"{BASE_URL}/v1/auth/register", params={
            "email": EMAIL,
            "password": PASSWORD,
            "first_name": FIRST_NAME,
            "last_name": LAST_NAME,
            "user_type": "patient"
        })
        if resp.status_code == 200:
            log("Registration successful", "PASS")
            return resp.json()
        elif resp.status_code == 400 and "already exists" in resp.text:
             log("User already exists, proceeding to login", "INFO")
        else:
            log(f"Registration failed: {resp.status_code} - {resp.text}", "FAIL")
            return None
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return None

    # 2. Login
    log(f"Logging in user: {EMAIL}...")
    try:
        resp = requests.post(f"{BASE_URL}/v1/auth/login/access-token", data={
            "username": EMAIL,
            "password": PASSWORD
        })
        if resp.status_code == 200:
            log("Login successful", "PASS")
            return resp.json()
        else:
            log(f"Login failed: {resp.status_code} - {resp.text}", "FAIL")
            return None
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return None

def test_assessment(token):
    log("\n=== Testing Assessment V2 Endpoints ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Start Session
    log("Starting Assessment Session...")
    session_id = None
    try:
        resp = requests.post(f"{BASE_URL}/v2/assessment/start", json={
            "patient_id": "current-user" # Use placeholder as per frontend
        }, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            session_id = data.get("session_id")
            log(f"Session Started: {session_id}", "PASS")
            log(f"Therapist Greeting: {data.get('response')}", "INFO")
        else:
            log(f"Start Session failed: {resp.status_code} - {resp.text}", "FAIL")
            return None
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return None

    # 2. Send Message
    if session_id:
        log("Sending Message: 'I feel anxious'...")
        try:
            resp = requests.post(f"{BASE_URL}/v2/assessment/message", json={
                "session_id": session_id,
                "patient_id": "current-user",
                "message": "I feel anxious about my job"
            }, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                log(f"Message Processed. Phase: {data.get('phase')}", "PASS")
                log(f"Therapist Response: {data.get('response')}", "INFO")
            else:
                log(f"Send Message failed: {resp.status_code} - {resp.text}", "FAIL")
        except Exception as e:
             log(f"Connection failed: {e}", "FAIL")

def test_booking(token, specialist_id):
    log("\n=== Testing Booking Endpoints ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get Slots
    log(f"Fetching slots for Specialist {specialist_id}...")
    try:
        resp = requests.get(f"{BASE_URL}/v1/appointments/slots/{specialist_id}", headers=headers)
        if resp.status_code == 200:
            slots = resp.json()
            log(f"Slots fetched: {len(slots)} available", "PASS")
            
            # 2. Book Slot (if slots available)
            if slots:
                slot = slots[0]
                log(f"Booking slot: {slot['date']} {slot['time']}...")
                resp = requests.post(f"{BASE_URL}/v1/appointments/book", json={
                    "specialist_id": specialist_id,
                    "date": slot['date'], # Assuming format is correct from API
                    "time": slot['time'],
                    "notes": "Test booking"
                }, headers=headers)
                
                if resp.status_code == 200:
                    log("Booking successful", "PASS")
                else:
                    log(f"Booking failed: {resp.status_code} - {resp.text}", "FAIL")
        else:
             log(f"Get Slots failed: {resp.status_code} - {resp.text}", "FAIL")
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")

def register_specialist():
    email = f"test_spec_{uuid.uuid4().hex[:8]}@example.com"
    log(f"Registering specialist: {email}...")
    try:
        resp = requests.post(f"{BASE_URL}/v1/auth/register", params={
            "email": email,
            "password": PASSWORD,
            "first_name": "Dr. Test",
            "last_name": "Specialist",
            "user_type": "specialist"
        })
        if resp.status_code == 200:
            data = resp.json()
            # The register response returns 'user_id' but we need 'specialist_id' (profile id).
            # The test-token endpoint gives us the profile ID.
            token = data["access_token"]
            return token
        else:
            log(f"Specialist registration failed: {resp.status_code}", "FAIL")
            return None
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return None

def get_specialist_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/v1/auth/test-token", headers=headers)
    if resp.status_code == 200:
        return resp.json().get("specialist_id")
    return None

if __name__ == "__main__":
    log("Verifying API Contracts for Frontend Integration...")
    
    # Check Server
    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        log("Backend server is not running on port 8000. Please start it.", "FAIL")
        sys.exit(1)

    auth_data = test_auth()
    if auth_data and "access_token" in auth_data:
        token = auth_data["access_token"]
        test_assessment(token)
        
        # Setup Specialist for Booking Test
        spec_token = register_specialist()
        if spec_token:
            spec_id = get_specialist_id(spec_token)
            if spec_id:
                log(f"Created Specialist for testing: {spec_id}", "INFO")
                test_booking(token, spec_id)
            else:
                log("Could not get specialist ID", "FAIL")
        else:
            log("Skipping Booking test due to specialist auth failure", "FAIL")
    else:
        log("Skipping further tests due to auth failure", "FAIL")
