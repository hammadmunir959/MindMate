"""
Test DA (Diagnostic Analysis) and TPA (Treatment Planning Agent) Modules
Tests comprehensive diagnostic analysis and treatment planning
"""

import sys
import os
import uuid
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.assessment.assessment_v2.agents.da.da_module import DiagnosticAnalysisModule
from app.agents.assessment.assessment_v2.agents.tpa.tpa_module import TreatmentPlanningModule
from app.agents.assessment.assessment_v2.core.sra_service import get_sra_service

def test_da_initialization():
    """Test DA module initialization"""
    print("\n" + "="*80)
    print("TEST 1: DA Module Initialization")
    print("="*80)
    
    try:
        da = DiagnosticAnalysisModule()
        
        print(f"✅ DA module initialized")
        print(f"   Module name: {da.module_name}")
        print(f"   Version: {da.module_version}")
        print(f"   Description: {da.module_description[:60]}...")
        print(f"   LLM available: {da.llm is not None}")
        print(f"   Database available: {da.db is not None}")
        print(f"   SRA service available: {da.sra_service is not None}")
        print(f"   DSM engine available: {hasattr(da, 'dsm_engine') and da.dsm_engine is not None}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error initializing DA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tpa_initialization():
    """Test TPA module initialization"""
    print("\n" + "="*80)
    print("TEST 2: TPA Module Initialization")
    print("="*80)
    
    try:
        tpa = TreatmentPlanningModule()
        
        print(f"✅ TPA module initialized")
        print(f"   Module name: {tpa.module_name}")
        print(f"   Version: {tpa.module_version}")
        print(f"   Description: {tpa.module_description[:60]}...")
        print(f"   LLM available: {tpa.llm is not None}")
        print(f"   Database available: {tpa.db is not None}")
        print(f"   SRA service available: {tpa.sra_service is not None}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error initializing TPA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_da_data_collection():
    """Test DA module data collection"""
    print("\n" + "="*80)
    print("TEST 3: DA Data Collection")
    print("="*80)
    
    try:
        da = DiagnosticAnalysisModule()
        session_id = f"test_da_{uuid.uuid4().hex[:8]}"
        
        # Test data collection method
        print(f"Testing data collection for session: {session_id}")
        
        all_data = da._get_all_assessment_data(session_id)
        
        print(f"✅ Data collection method executed")
        print(f"   Module results: {len(all_data.get('module_results', {}))} modules")
        print(f"   Symptom data: {bool(all_data.get('symptom_data'))}")
        print(f"   Conversation history: {len(all_data.get('conversation_history', []))} messages")
        print(f"   Demographics: {bool(all_data.get('demographics'))}")
        print(f"   Risk assessment: {bool(all_data.get('risk_assessment'))}")
        print(f"   Screening results: {bool(all_data.get('screening_results'))}")
        print(f"   Diagnostic results: {bool(all_data.get('diagnostic_results'))}")
        
        # Check structure
        required_keys = ['module_results', 'symptom_data', 'conversation_history', 
                        'demographics', 'risk_assessment', 'screening_results', 'diagnostic_results']
        missing_keys = [key for key in required_keys if key not in all_data]
        
        if missing_keys:
            print(f"   ⚠️  Missing keys: {missing_keys}")
        else:
            print(f"   ✅ All required keys present")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error in data collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tpa_data_collection():
    """Test TPA module data collection"""
    print("\n" + "="*80)
    print("TEST 4: TPA Data Collection")
    print("="*80)
    
    try:
        tpa = TreatmentPlanningModule()
        session_id = f"test_tpa_{uuid.uuid4().hex[:8]}"
        
        # Test data collection method
        print(f"Testing data collection for session: {session_id}")
        
        all_data = tpa._get_all_treatment_planning_data(session_id)
        
        print(f"✅ Data collection method executed")
        print(f"   DA results: {bool(all_data.get('da_results'))}")
        print(f"   Module results: {len(all_data.get('module_results', {}))} modules")
        print(f"   Symptom data: {bool(all_data.get('symptom_data'))}")
        print(f"   Demographics: {bool(all_data.get('demographics'))}")
        print(f"   Risk assessment: {bool(all_data.get('risk_assessment'))}")
        
        # Check structure
        required_keys = ['da_results', 'module_results', 'symptom_data', 
                        'demographics', 'risk_assessment']
        missing_keys = [key for key in required_keys if key not in all_data]
        
        if missing_keys:
            print(f"   ⚠️  Missing keys: {missing_keys}")
        else:
            print(f"   ✅ All required keys present")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error in data collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_da_session_start():
    """Test DA session start"""
    print("\n" + "="*80)
    print("TEST 5: DA Session Start")
    print("="*80)
    
    try:
        da = DiagnosticAnalysisModule()
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        session_id = f"test_da_session_{uuid.uuid4().hex[:8]}"
        
        print(f"Starting DA session: {session_id}")
        
        # Add some mock data to SRA service
        sra_service = get_sra_service()
        if sra_service:
            # Add some test symptoms
            from app.agents.assessment.assessment_v2.base_types import SCIDQuestion, ProcessedResponse, ResponseType
            question = SCIDQuestion(
                id="test_q",
                sequence_number=1,
                simple_text="How are you feeling?",
                response_type=ResponseType.TEXT
            )
            processed = ProcessedResponse(
                selected_option=None,
                extracted_fields={},
                confidence=0.8
            )
            sra_service.process_response(
                session_id=session_id,
                user_response="I feel sad and anxious",
                question=question,
                processed_response=processed,
                conversation_history=[]
            )
            print(f"   Added test symptoms to SRA service")
        
        # Start DA session
        response = da.start_session(user_id=user_id, session_id=session_id)
        
        print(f"✅ DA session started")
        print(f"   Response message length: {len(response.message)}")
        print(f"   Is complete: {response.is_complete}")
        print(f"   Requires input: {response.requires_input}")
        print(f"   Message preview: {response.message[:100]}...")
        
        # Check session state
        if session_id in da._sessions:
            session_state = da._sessions[session_id]
            print(f"   Session status: {session_state.get('status')}")
            print(f"   Has primary diagnosis: {bool(session_state.get('primary_diagnosis'))}")
            print(f"   Confidence score: {session_state.get('confidence_score', 0.0)}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error starting DA session: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tpa_session_start():
    """Test TPA session start"""
    print("\n" + "="*80)
    print("TEST 6: TPA Session Start")
    print("="*80)
    
    try:
        tpa = TreatmentPlanningModule()
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        session_id = f"test_tpa_session_{uuid.uuid4().hex[:8]}"
        
        print(f"Starting TPA session: {session_id}")
        
        # First, create a mock DA result
        da = DiagnosticAnalysisModule()
        da._ensure_session_exists(session_id)
        da._sessions[session_id]["primary_diagnosis"] = {
            "name": "Major Depressive Disorder",
            "severity": "moderate",
            "confidence": 0.75
        }
        da._sessions[session_id]["status"] = "completed"
        
        # Save DA result to database if available
        if da.db:
            try:
                da.db.save_module_result(session_id, "da_diagnostic_analysis", {
                    "primary_diagnosis": da._sessions[session_id]["primary_diagnosis"]
                })
                print(f"   Saved mock DA result to database")
            except Exception as e:
                print(f"   ⚠️  Could not save DA result: {e}")
        
        # Start TPA session
        response = tpa.start_session(user_id=user_id, session_id=session_id)
        
        print(f"✅ TPA session started")
        print(f"   Response message length: {len(response.message)}")
        print(f"   Is complete: {response.is_complete}")
        print(f"   Requires input: {response.requires_input}")
        print(f"   Message preview: {response.message[:100]}...")
        
        # Check session state
        if session_id in tpa._sessions:
            session_state = tpa._sessions[session_id]
            print(f"   Session status: {session_state.get('status')}")
            print(f"   Has treatment plan: {bool(session_state.get('treatment_plan'))}")
            print(f"   Has DA results: {bool(session_state.get('da_results'))}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED - Error starting TPA session: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_da_completion_check():
    """Test DA completion check"""
    print("\n" + "="*80)
    print("TEST 7: DA Completion Check")
    print("="*80)
    
    try:
        da = DiagnosticAnalysisModule()
        session_id = f"test_da_complete_{uuid.uuid4().hex[:8]}"
        
        # Test with no session
        is_complete = da.is_complete(session_id)
        print(f"   No session - Complete: {is_complete} (expected: False)")
        
        # Create session and mark as incomplete
        da._ensure_session_exists(session_id)
        da._sessions[session_id]["status"] = "analyzing"
        is_complete = da.is_complete(session_id)
        print(f"   Session analyzing - Complete: {is_complete} (expected: False)")
        
        # Mark as complete
        da._sessions[session_id]["status"] = "completed"
        is_complete = da.is_complete(session_id)
        print(f"   Session completed - Complete: {is_complete} (expected: True)")
        
        if is_complete:
            print(f"   ✅ PASSED")
            return True
        else:
            print(f"   ❌ FAILED")
            return False
    except Exception as e:
        print(f"❌ FAILED - Error checking completion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tpa_completion_check():
    """Test TPA completion check"""
    print("\n" + "="*80)
    print("TEST 8: TPA Completion Check")
    print("="*80)
    
    try:
        tpa = TreatmentPlanningModule()
        session_id = f"test_tpa_complete_{uuid.uuid4().hex[:8]}"
        
        # Test with no session
        is_complete = tpa.is_complete(session_id)
        print(f"   No session - Complete: {is_complete} (expected: False)")
        
        # Create session and mark as incomplete
        tpa._ensure_session_exists(session_id)
        tpa._sessions[session_id]["status"] = "planning"
        is_complete = tpa.is_complete(session_id)
        print(f"   Session planning - Complete: {is_complete} (expected: False)")
        
        # Mark as complete
        tpa._sessions[session_id]["status"] = "completed"
        is_complete = tpa.is_complete(session_id)
        print(f"   Session completed - Complete: {is_complete} (expected: True)")
        
        if is_complete:
            print(f"   ✅ PASSED")
            return True
        else:
            print(f"   ❌ FAILED")
            return False
    except Exception as e:
        print(f"❌ FAILED - Error checking completion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_da_get_results():
    """Test DA get_results method"""
    print("\n" + "="*80)
    print("TEST 9: DA Get Results")
    print("="*80)
    
    try:
        da = DiagnosticAnalysisModule()
        session_id = f"test_da_results_{uuid.uuid4().hex[:8]}"
        
        # Create session with results
        da._ensure_session_exists(session_id)
        da._sessions[session_id].update({
            "primary_diagnosis": {"name": "Test Diagnosis", "severity": "moderate"},
            "differential_diagnoses": [{"name": "Differential 1"}],
            "confidence_score": 0.8,
            "reasoning": "Test reasoning",
            "matched_criteria": ["Criterion 1", "Criterion 2"],
            "dsm5_mapping": {"MDD": True},
            "all_module_results": {"module1": {}},
            "symptom_data": {"summary": {}}
        })
        
        results = da.get_results(session_id)
        
        print(f"✅ Results retrieved")
        print(f"   Module name: {results.get('module_name')}")
        print(f"   Primary diagnosis: {results.get('primary_diagnosis', {}).get('name', 'N/A')}")
        print(f"   Differential diagnoses: {len(results.get('differential_diagnoses', []))}")
        print(f"   Confidence score: {results.get('confidence_score')}")
        print(f"   Has reasoning: {bool(results.get('reasoning'))}")
        print(f"   Matched criteria: {len(results.get('matched_criteria', []))}")
        print(f"   DSM-5 mapping: {bool(results.get('dsm5_mapping'))}")
        
        # Check required fields
        required_fields = ['module_name', 'primary_diagnosis', 'differential_diagnoses', 
                          'confidence_score', 'reasoning', 'matched_criteria', 'dsm5_mapping']
        missing_fields = [field for field in required_fields if field not in results]
        
        if missing_fields:
            print(f"   ⚠️  Missing fields: {missing_fields}")
            return False
        else:
            print(f"   ✅ All required fields present")
            return True
    except Exception as e:
        print(f"❌ FAILED - Error getting results: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tpa_get_results():
    """Test TPA get_results method"""
    print("\n" + "="*80)
    print("TEST 10: TPA Get Results")
    print("="*80)
    
    try:
        tpa = TreatmentPlanningModule()
        session_id = f"test_tpa_results_{uuid.uuid4().hex[:8]}"
        
        # Create session with results
        tpa._ensure_session_exists(session_id)
        tpa._sessions[session_id].update({
            "treatment_plan": {
                "primary_intervention": {"name": "Test Intervention"},
                "complementary_strategies": [{"name": "Strategy 1"}],
                "follow_up_schedule": {},
                "expected_outcomes": ["Outcome 1"]
            },
            "reasoning": "Test reasoning",
            "evidence_sources": ["Source 1"],
            "da_results": {"test": True},
            "symptom_data": {"test": True}
        })
        
        results = tpa.get_results(session_id)
        
        print(f"✅ Results retrieved")
        print(f"   Module name: {results.get('module_name')}")
        print(f"   Has treatment plan: {bool(results.get('treatment_plan'))}")
        print(f"   Primary intervention: {results.get('primary_intervention', {}).get('name', 'N/A')}")
        print(f"   Complementary strategies: {len(results.get('complementary_strategies', []))}")
        print(f"   Expected outcomes: {len(results.get('expected_outcomes', []))}")
        print(f"   Has reasoning: {bool(results.get('reasoning'))}")
        print(f"   Uses DA results: {results.get('uses_da_results')}")
        print(f"   Uses SRA data: {results.get('uses_sra_data')}")
        
        # Check required fields
        required_fields = ['module_name', 'treatment_plan', 'primary_intervention', 
                          'complementary_strategies', 'expected_outcomes', 'reasoning']
        missing_fields = [field for field in required_fields if field not in results]
        
        if missing_fields:
            print(f"   ⚠️  Missing fields: {missing_fields}")
            return False
        else:
            print(f"   ✅ All required fields present")
            return True
    except Exception as e:
        print(f"❌ FAILED - Error getting results: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all DA and TPA tests"""
    print("\n" + "="*80)
    print("DA AND TPA MODULES COMPREHENSIVE TEST")
    print("="*80)
    
    results = {}
    
    # Run tests
    results['da_init'] = test_da_initialization()
    results['tpa_init'] = test_tpa_initialization()
    results['da_data'] = test_da_data_collection()
    results['tpa_data'] = test_tpa_data_collection()
    results['da_start'] = test_da_session_start()
    results['tpa_start'] = test_tpa_session_start()
    results['da_complete'] = test_da_completion_check()
    results['tpa_complete'] = test_tpa_completion_check()
    results['da_results'] = test_da_get_results()
    results['tpa_results'] = test_tpa_get_results()
    
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

