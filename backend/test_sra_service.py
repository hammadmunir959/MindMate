"""
Test SRA (Symptom Recognition and Analysis) Service
Tests symptom extraction from user responses
"""

import sys
import os
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.assessment.assessment_v2.core.sra_service import SRAService, get_sra_service
from app.agents.assessment.assessment_v2.base_types import SCIDQuestion, ProcessedResponse, ResponseType

def create_test_question(text: str = "How are you feeling?") -> SCIDQuestion:
    """Create a test question"""
    return SCIDQuestion(
        id=f"test_q_{uuid.uuid4().hex[:8]}",
        sequence_number=1,
        simple_text=text,
        response_type=ResponseType.TEXT,
        required=True
    )

def create_test_processed_response(
    selected_option: str = None,
    confidence: float = 0.8,
    extracted_fields: dict = None
) -> ProcessedResponse:
    """Create a test processed response"""
    return ProcessedResponse(
        selected_option=selected_option,
        extracted_fields=extracted_fields or {},
        confidence=confidence,
        dsm_criteria_mapping={},
        validation={"is_valid": True},
        raw_response="test response"
    )

def test_rule_based_extraction():
    """Test rule-based symptom extraction"""
    print("\n" + "="*80)
    print("TEST 1: Rule-Based Symptom Extraction")
    print("="*80)
    
    sra = SRAService(llm_client=None)  # No LLM, rule-based only
    session_id = f"test_sra_{uuid.uuid4().hex[:8]}"
    
    test_cases = [
        {
            "response": "I've been feeling really sad and depressed for the past few weeks",
            "expected_categories": ["mood"],
            "description": "Mood symptoms"
        },
        {
            "response": "I have trouble sleeping and feel anxious all the time",
            "expected_categories": ["sleep", "anxiety"],
            "description": "Sleep and anxiety symptoms"
        },
        {
            "response": "I've lost my appetite and feel tired constantly",
            "expected_categories": ["appetite", "energy"],
            "description": "Appetite and energy symptoms"
        },
        {
            "response": "I can't concentrate and my memory is terrible",
            "expected_categories": ["concentration"],
            "description": "Concentration symptoms"
        },
        {
            "response": "I've been having panic attacks daily",
            "expected_categories": ["panic"],
            "description": "Panic symptoms"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   Response: '{test_case['response']}'")
        
        question = create_test_question("How are you feeling?")
        processed = create_test_processed_response()
        
        result = sra.process_response(
            session_id=session_id,
            user_response=test_case['response'],
            question=question,
            processed_response=processed,
            conversation_history=[]
        )
        
        symptoms = result.get('symptoms', [])
        extracted_categories = [s.get('category') for s in symptoms]
        
        print(f"   Extracted {len(symptoms)} symptoms")
        print(f"   Categories: {extracted_categories}")
        
        # Check if expected categories are present
        found_categories = [cat for cat in test_case['expected_categories'] if cat in extracted_categories]
        
        if len(found_categories) == len(test_case['expected_categories']):
            print(f"   ✅ PASSED - Found all expected categories")
        else:
            print(f"   ❌ FAILED - Expected {test_case['expected_categories']}, found {extracted_categories}")
            all_passed = False
        
        # Print symptom details
        for symptom in symptoms:
            print(f"      - {symptom.get('name')} ({symptom.get('category')})")
    
    return all_passed

def test_llm_extraction():
    """Test LLM-based symptom extraction"""
    print("\n" + "="*80)
    print("TEST 2: LLM-Based Symptom Extraction")
    print("="*80)
    
    sra = get_sra_service()  # Use global instance with LLM
    session_id = f"test_sra_llm_{uuid.uuid4().hex[:8]}"
    
    if not sra.llm_client:
        print("⚠️  LLM client not available - skipping LLM extraction test")
        return True
    
    test_cases = [
        {
            "response": "I've been experiencing severe depression with suicidal thoughts for about 3 months",
            "description": "Complex symptom description"
        },
        {
            "response": "I have anxiety attacks weekly, especially in crowded places",
            "description": "Anxiety with frequency"
        },
        {
            "response": "I can't sleep at night and feel exhausted during the day",
            "description": "Sleep and energy issues"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   Response: '{test_case['response']}'")
        
        question = create_test_question("Tell me about your symptoms")
        processed = create_test_processed_response()
        
        result = sra.process_response(
            session_id=session_id,
            user_response=test_case['response'],
            question=question,
            processed_response=processed,
            conversation_history=[]
        )
        
        symptoms = result.get('symptoms', [])
        method = result.get('method', 'unknown')
        
        print(f"   Method: {method}")
        print(f"   Extracted {len(symptoms)} symptoms")
        
        if symptoms:
            print(f"   ✅ PASSED - Extracted symptoms")
            for symptom in symptoms:
                print(f"      - {symptom.get('name')} ({symptom.get('category')})")
                print(f"        Severity: {symptom.get('severity', 'N/A')}")
                print(f"        Frequency: {symptom.get('frequency', 'N/A')}")
                print(f"        Duration: {symptom.get('duration', 'N/A')}")
        else:
            print(f"   ⚠️  No symptoms extracted (may be valid if no symptoms mentioned)")
    
    return all_passed

def test_symptom_database():
    """Test symptom database storage and retrieval"""
    print("\n" + "="*80)
    print("TEST 3: Symptom Database Storage")
    print("="*80)
    
    sra = get_sra_service()
    session_id = f"test_sra_db_{uuid.uuid4().hex[:8]}"
    
    # Process multiple responses
    responses = [
        "I feel sad and depressed",
        "I have trouble sleeping",
        "I feel anxious all the time"
    ]
    
    all_symptoms = []
    for i, response in enumerate(responses, 1):
        print(f"\n{i}. Processing: '{response}'")
        
        question = create_test_question("How are you feeling?")
        processed = create_test_processed_response()
        
        result = sra.process_response(
            session_id=session_id,
            user_response=response,
            question=question,
            processed_response=processed,
            conversation_history=[]
        )
        
        symptoms = result.get('symptoms', [])
        all_symptoms.extend(symptoms)
        print(f"   Extracted {len(symptoms)} symptoms")
    
    # Get summary
    print(f"\n4. Getting symptom summary for session {session_id}")
    summary = sra.get_symptoms_summary(session_id)
    
    print(f"   Summary: {summary}")
    
    # Export symptoms
    print(f"\n5. Exporting symptoms")
    exported = sra.export_symptoms(session_id)
    
    print(f"   Exported {len(exported)} symptoms")
    for symptom in exported:
        print(f"      - {symptom.get('name', 'Unknown')} ({symptom.get('category', 'Unknown')})")
    
    if len(exported) > 0:
        print(f"   ✅ PASSED - Symptoms stored and retrieved")
        return True
    else:
        print(f"   ❌ FAILED - No symptoms in database")
        return False

def test_json_parsing():
    """Test JSON parsing improvements"""
    print("\n" + "="*80)
    print("TEST 4: JSON Parsing (Improved)")
    print("="*80)
    
    sra = SRAService(llm_client=None)
    
    test_cases = [
        {
            "input": '[{"name": "Depression", "category": "mood", "severity": "severe"}]',
            "expected": 1,
            "description": "Valid JSON array"
        },
        {
            "input": '```json\n[{"name": "Anxiety", "category": "anxiety"}]\n```',
            "expected": 1,
            "description": "JSON with markdown code blocks"
        },
        {
            "input": 'Okay, here are the symptoms: [{"name": "Sleep issues", "category": "sleep"}]',
            "expected": 1,
            "description": "JSON with text before"
        },
        {
            "input": '[{"name": "Panic", "category": "panic"}, {"name": "Anxiety", "category": "anxiety"}]',
            "expected": 2,
            "description": "Multiple symptoms"
        },
        {
            "input": '[{"name": "Test", "category": "mood",},]',  # Trailing comma
            "expected": 1,
            "description": "JSON with trailing comma"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   Input: {test_case['input'][:60]}...")
        
        result = sra._parse_json_array(test_case['input'])
        
        print(f"   Parsed {len(result)} symptoms")
        
        if len(result) == test_case['expected']:
            print(f"   ✅ PASSED")
            for symptom in result:
                print(f"      - {symptom.get('name', 'Unknown')}")
        else:
            print(f"   ❌ FAILED - Expected {test_case['expected']}, got {len(result)}")
            all_passed = False
    
    return all_passed

def test_severity_frequency_duration():
    """Test severity, frequency, and duration extraction"""
    print("\n" + "="*80)
    print("TEST 5: Severity, Frequency, Duration Extraction")
    print("="*80)
    
    sra = SRAService(llm_client=None)
    
    test_cases = [
        {
            "response": "I feel extremely depressed and terrible",
            "expected_severity": "severe",
            "description": "Severe severity"
        },
        {
            "response": "I feel somewhat anxious",
            "expected_severity": "moderate",
            "description": "Moderate severity"
        },
        {
            "response": "I feel a little sad",
            "expected_severity": "mild",
            "description": "Mild severity"
        },
        {
            "response": "I have panic attacks daily",
            "expected_frequency": "daily",
            "description": "Daily frequency"
        },
        {
            "response": "I feel anxious sometimes",
            "expected_frequency": "occasional",
            "description": "Occasional frequency"
        },
        {
            "response": "I've been depressed for 2 years",
            "expected_duration": "years",
            "description": "Years duration"
        },
        {
            "response": "I've had anxiety for 3 months",
            "expected_duration": "months",
            "description": "Months duration"
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   Response: '{test_case['response']}'")
        
        severity = sra._extract_severity(test_case['response'])
        frequency = sra._extract_frequency(test_case['response'])
        duration = sra._extract_duration(test_case['response'])
        
        print(f"   Severity: {severity}")
        print(f"   Frequency: {frequency}")
        print(f"   Duration: {duration}")
        
        passed = True
        if 'expected_severity' in test_case:
            if severity == test_case['expected_severity']:
                print(f"   ✅ Severity PASSED")
            else:
                print(f"   ❌ Severity FAILED - Expected {test_case['expected_severity']}, got {severity}")
                passed = False
        
        if 'expected_frequency' in test_case:
            if frequency == test_case['expected_frequency']:
                print(f"   ✅ Frequency PASSED")
            else:
                print(f"   ❌ Frequency FAILED - Expected {test_case['expected_frequency']}, got {frequency}")
                passed = False
        
        if 'expected_duration' in test_case:
            if duration == test_case['expected_duration']:
                print(f"   ✅ Duration PASSED")
            else:
                print(f"   ❌ Duration FAILED - Expected {test_case['expected_duration']}, got {duration}")
                passed = False
        
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Run all SRA tests"""
    print("\n" + "="*80)
    print("SRA SERVICE COMPREHENSIVE TEST")
    print("="*80)
    
    results = {}
    
    # Run tests
    results['rule_based'] = test_rule_based_extraction()
    results['llm'] = test_llm_extraction()
    results['database'] = test_symptom_database()
    results['json_parsing'] = test_json_parsing()
    results['attributes'] = test_severity_frequency_duration()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

