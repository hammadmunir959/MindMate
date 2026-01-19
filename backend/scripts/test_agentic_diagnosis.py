"""
Agentic Diagnosis Test Script
=============================
Tests the optimized 3-5 step diagnosis flow.
"""

import requests
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"

def test_agentic_diagnosis():
    """Test the new agentic diagnosis system"""
    
    # 1. Authenticate
    logger.info("Authenticating...")
    auth_data = {
        "email": f"agentic_test_{int(time.time())}@test.com",
        "password": "Test123!@#",
        "first_name": "Agentic",
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
        "I have no energy and just stay in bed all day. I've lost interest in everything.",
        "I can't sleep at night, I've lost my appetite, and I feel worthless."
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
        logger.info(f"  Response received")
        time.sleep(2)  # Allow SRA to process
    
    # 4. Trigger Agentic Diagnosis
    logger.info("\n" + "="*50)
    logger.info("TRIGGERING AGENTIC DIAGNOSIS (should be 3-5 steps)")
    logger.info("="*50)
    
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/assessment/diagnose",
        headers=headers,
        json={"session_id": session_id, "message": "diagnose"}
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code != 200:
        logger.error(f"Diagnosis failed: {response.text}")
        return
    
    result = response.json()
    
    logger.info(f"\n⏱️  Diagnosis completed in {elapsed:.1f} seconds")
    logger.info(f"📊 Result: {json.dumps(result, indent=2)}")
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    
    diagnoses = result.get("diagnoses", [])
    if diagnoses:
        for d in diagnoses:
            logger.info(f"  ✓ {d.get('disorder_name')} ({d.get('severity')} severity)")
            logger.info(f"    Criteria: {d.get('met_count')}/{d.get('required_count')}")
    else:
        logger.info("  No diagnoses confirmed")
    
    logger.info(f"\n  Steps taken: {result.get('steps_taken', 'N/A')}")
    logger.info(f"  Categories: {result.get('metadata', {}).get('categories_screened', [])}")
    logger.info(f"  Candidates: {result.get('metadata', {}).get('candidates_evaluated', [])}")
    
    report = result.get("clinical_report", "")
    if report:
        logger.info(f"\n📋 Clinical Report:\n  {report[:200]}...")
    
    recommendations = result.get("recommendations", [])
    if recommendations:
        logger.info("\n🎯 Recommendations:")
        for rec in recommendations[:3]:
            logger.info(f"  • {rec}")
    
    logger.info("\n✅ Agentic diagnosis test complete!")


if __name__ == "__main__":
    test_agentic_diagnosis()
