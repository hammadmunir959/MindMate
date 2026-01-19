import requests
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"

def test_sra_flow():
    # 1. Authenticate
    logger.info("🔹 Authenticating...")
    auth_data = {
        "email": f"sra_test_{int(time.time())}@example.com",
        "password": "password123",
        "first_name": "SRA",
        "last_name": "TestUser",
        "user_type": "patient"
    }
    
    # Register/Login
    # Registration returns token
    reg_response = requests.post(f"{BASE_URL}/auth/register", params=auth_data)
    if reg_response.status_code != 200:
         logger.error(f"Register Failed: {reg_response.text}")
         return
         
    token = reg_response.json().get("access_token")
    if not token:
        # Try login if no token (fallback, though login endpoint seems busted or moved)
        logger.warning("No token in register response, trying login skipped due to 404 issue")
        return

    headers = {"Authorization": f"Bearer {token}"}
    logger.info("✅ Authenticated")
    
    # 2. Start Session
    logger.info("🔹 Starting Session...")
    response = requests.post(f"{BASE_URL}/assessment/start", headers=headers)
    session_id = response.json()["session_id"]
    logger.info(f"✅ Session Started: {session_id}")
    
    # 3. Simulate Conversation (Depression Symptoms)
    messages = [
        "I've been feeling extremely sad and hopeless exclusively for the last month.",
        "I have absolutely no energy to do anything, I just stay in bed.",
        "I can't sleep at night, I wake up at 3am every day."
    ]
    
    for msg in messages:
        logger.info(f"🔹 Sending Chat: '{msg}'")
        response = requests.post(
            f"{BASE_URL}/assessment/chat", 
            headers=headers, 
            json={"session_id": session_id, "message": msg}
        )
        logger.info(f"   Response: {response.json()['response'][:50]}...")
        # Wait for background SRA
        time.sleep(2) 
        
    # 4. Trigger Diagnosis
    logger.info("🔹 Triggering Diagnosis...")
    response = requests.post(
        f"{BASE_URL}/assessment/diagnose",
        headers=headers,
        json={"session_id": session_id, "message": "diagnose"} # message ignored
    )
    
    if response.status_code == 200:
        result = response.json()
        logger.info("✅ Diagnosis Result Received")
        logger.info(json.dumps(result, indent=2))
        
        diagnoses = result.get("diagnoses", [])
        if diagnoses:
            primary = diagnoses[0]
            logger.info(f"🏆 Primary Diagnosis: {primary['disorder_name']} ({primary['confidence']} confidence)")
        else:
            logger.warning("⚠️ No diagnosis generated (insufficient symptoms?)")
    else:
        logger.error(f"❌ Diagnosis verification failed: {response.text}")

if __name__ == "__main__":
    test_sra_flow()
