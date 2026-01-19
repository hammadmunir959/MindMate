"""
Matcher Flow Test Script
========================
Tests the complete flow: Chat -> Diagnose -> Match
"""

import requests
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"

def test_matcher_flow():
    """Test full assessment -> diagnosis -> matching flow"""
    
    # 1. Authenticate
    logger.info("Authenticating...")
    auth_data = {
        "email": f"matcher_test_{int(time.time())}@test.com",
        "password": "Test123!@#",
        "first_name": "Matcher",
        "last_name": "Test",
        "user_type": "patient"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", params=auth_data)
    if response.status_code != 200:
        logger.error(f"Registration failed: {response.text}")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("Authenticated successfully")
    
    # 2. Start Session
    logger.info("Starting session...")
    response = requests.post(f"{BASE_URL}/assessment/start", headers=headers)
    if response.status_code != 200:
        logger.error(f"Start session failed: {response.text}")
        return
    
    session_id = response.json().get("session_id")
    logger.info(f"Session started: {session_id}")
    
    # 3. Send chat messages (symptoms for MDD)
    messages = [
        "I've been feeling extremely sad and hopeless for weeks.",
        "I have no energy and just stay in bed all day.",
        "I can't sleep at night and have lost my appetite."
    ]
    
    for msg in messages:
        logger.info(f"Sending: '{msg[:50]}...'")
        response = requests.post(
            f"{BASE_URL}/assessment/chat",
            headers=headers,
            json={"session_id": session_id, "message": msg}
        )
        if response.status_code != 200:
            logger.error(f"Chat failed: {response.text}")
            return
        logger.info(f"  Response: {response.json().get('response', '')[:50]}...")
        time.sleep(2)  # Allow SRA to process
    
    # 4. Trigger Diagnosis
    logger.info("Triggering diagnosis...")
    response = requests.post(
        f"{BASE_URL}/assessment/diagnose",
        headers=headers,
        json={"session_id": session_id, "message": "diagnose"}  # Added message field
    )
    
    if response.status_code != 200:
        logger.error(f"Diagnosis failed: {response.text}")
        return
    
    diagnosis = response.json()
    logger.info(f"Diagnosis result: {json.dumps(diagnosis, indent=2)}")
    
    if not diagnosis.get("diagnoses"):
        logger.warning("No diagnosis generated - insufficient symptoms?")
        return
    
    # 5. Trigger Matching
    logger.info("Triggering specialist matching...")
    response = requests.post(
        f"{BASE_URL}/assessment/match",
        headers=headers,
        json={"session_id": session_id, "message": "match"}  # Added message field
    )
    
    if response.status_code != 200:
        logger.error(f"Matching failed: {response.text}")
        return
    
    matches = response.json()
    logger.info(f"Match result: {json.dumps(matches, indent=2)}")
    
    # 6. Verify stored matches
    logger.info("Fetching stored matches...")
    response = requests.get(
        f"{BASE_URL}/assessment/matches/{session_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        stored = response.json()
        logger.info(f"Stored matches: {json.dumps(stored, indent=2)}")
    else:
        logger.warning(f"Could not fetch stored matches: {response.text}")
    
    logger.info("Matcher flow test complete!")


if __name__ == "__main__":
    test_matcher_flow()
