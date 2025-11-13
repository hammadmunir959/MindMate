"""
Comprehensive Assessment Workflow Test
Tests the entire assessment workflow step by step and identifies issues/flaws
"""

import sys
import os
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.assessment.assessment_v2.moderator import AssessmentModerator
from app.agents.assessment.assessment_v2.config import get_module_sequence

class WorkflowTester:
    """Comprehensive workflow tester"""
    
    def __init__(self):
        self.moderator: Optional[AssessmentModerator] = None
        self.session_id: Optional[str] = None
        self.user_id = "test_user_123"
        self.issues: List[Dict[str, Any]] = []
        self.test_results: List[Dict[str, Any]] = []
        self.current_module: Optional[str] = None
        
    def log_issue(self, severity: str, module: str, description: str, error: Optional[Exception] = None):
        """Log an issue found during testing"""
        issue = {
            "severity": severity,  # "critical", "high", "medium", "low"
            "module": module,
            "description": description,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        }
        self.issues.append(issue)
        print(f"\n⚠️  [{severity.upper()}] {module}: {description}")
        if error:
            print(f"   Error: {error}")
    
    def log_test(self, step: str, status: str, details: str = ""):
        """Log a test step"""
        result = {
            "step": step,
            "status": status,  # "pass", "fail", "warning"
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        print(f"{status_icon} {step}: {details}")
    
    def test_initialization(self):
        """Test 1: Initialize AssessmentModerator"""
        print("\n" + "="*80)
        print("TEST 1: Initialization")
        print("="*80)
        
        try:
            self.moderator = AssessmentModerator()
            if not self.moderator:
                self.log_issue("critical", "initialization", "Failed to create AssessmentModerator")
                self.log_test("Initialization", "fail", "Moderator is None")
                return False
            
            if len(self.moderator.modules) == 0:
                self.log_issue("critical", "initialization", "No modules loaded")
                self.log_test("Initialization", "fail", "No modules available")
                return False
            
            self.log_test("Initialization", "pass", f"Loaded {len(self.moderator.modules)} modules")
            print(f"   Modules: {', '.join(list(self.moderator.modules.keys())[:5])}...")
            return True
            
        except Exception as e:
            self.log_issue("critical", "initialization", "Exception during initialization", e)
            self.log_test("Initialization", "fail", f"Exception: {e}")
            traceback.print_exc()
            return False
    
    def test_start_assessment(self):
        """Test 2: Start Assessment Session"""
        print("\n" + "="*80)
        print("TEST 2: Start Assessment")
        print("="*80)
        
        try:
            import uuid
            self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"
            
            greeting = self.moderator.start_assessment(
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            if not greeting:
                self.log_issue("high", "start_assessment", "No greeting returned")
                self.log_test("Start Assessment", "fail", "Empty greeting")
                return False
            
            if len(greeting.strip()) < 10:
                self.log_issue("medium", "start_assessment", f"Very short greeting: '{greeting}'")
            
            # Check session state
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_issue("critical", "start_assessment", "Session state not created")
                self.log_test("Start Assessment", "fail", "No session state")
                return False
            
            self.current_module = session_state.current_module
            if not self.current_module:
                self.log_issue("high", "start_assessment", "No current module set")
                self.log_test("Start Assessment", "fail", "No current module")
                return False
            
            expected_start = get_module_sequence()[0]
            if self.current_module != expected_start:
                self.log_issue("medium", "start_assessment", 
                             f"Starting module mismatch: expected '{expected_start}', got '{self.current_module}'")
            
            self.log_test("Start Assessment", "pass", 
                         f"Session started, current module: {self.current_module}")
            print(f"   Greeting: {greeting[:100]}...")
            return True
            
        except Exception as e:
            self.log_issue("critical", "start_assessment", "Exception during start", e)
            self.log_test("Start Assessment", "fail", f"Exception: {e}")
            traceback.print_exc()
            return False
    
    def test_module_workflow(self, module_name: str, test_responses: List[str]) -> bool:
        """Test a specific module with test responses"""
        print("\n" + "="*80)
        print(f"TEST: Module '{module_name}'")
        print("="*80)
        
        if module_name not in self.moderator.modules:
            self.log_issue("high", module_name, f"Module not found in moderator")
            self.log_test(f"Module {module_name}", "fail", "Module not available")
            return False
        
        try:
            # Verify we're in the right module
            session_state = self.moderator.get_session_state(self.session_id)
            if session_state.current_module != module_name:
                self.log_issue("medium", module_name, 
                             f"Module mismatch: expected '{module_name}', current is '{session_state.current_module}'")
                # Try to continue anyway
            
            module = self.moderator.modules[module_name]
            question_count = 0
            max_questions = 20  # Safety limit
            
            for i, response_text in enumerate(test_responses):
                if question_count >= max_questions:
                    self.log_issue("medium", module_name, f"Reached max questions limit ({max_questions})")
                    break
                
                print(f"\n  Question {question_count + 1}: Sending response: '{response_text}'")
                
                try:
                    result = self.moderator.process_message(
                        user_id=self.user_id,
                        session_id=self.session_id,
                        message=response_text
                    )
                    
                    if not result:
                        self.log_issue("high", module_name, f"Empty response to message {i+1}")
                        self.log_test(f"{module_name} - Response {i+1}", "fail", "Empty response")
                        return False
                    
                    if len(result.strip()) < 5:
                        self.log_issue("medium", module_name, f"Very short response: '{result}'")
                    
                    print(f"  Response: {result[:150]}...")
                    question_count += 1
                    
                    # Check if module is complete
                    session_state = self.moderator.get_session_state(self.session_id)
                    if not session_state:
                        self.log_issue("critical", module_name, "Session state lost")
                        return False
                    
                    # Check if we moved to next module
                    if session_state.current_module != module_name:
                        print(f"  Module completed! Moved to: {session_state.current_module}")
                        self.current_module = session_state.current_module
                        self.log_test(f"Module {module_name}", "pass", 
                                     f"Completed after {question_count} questions")
                        return True
                    
                except Exception as e:
                    self.log_issue("high", module_name, f"Error processing response {i+1}", e)
                    self.log_test(f"{module_name} - Response {i+1}", "fail", f"Exception: {e}")
                    traceback.print_exc()
                    return False
            
            # Check if module is complete after all responses
            session_state = self.moderator.get_session_state(self.session_id)
            if session_state and session_state.current_module == module_name:
                # Module not complete - check if it should be
                try:
                    is_complete = module.is_complete(self.session_id)
                    if not is_complete:
                        self.log_issue("medium", module_name, 
                                     f"Module not complete after {len(test_responses)} responses")
                        self.log_test(f"Module {module_name}", "warning", 
                                     f"Not complete after test responses")
                except Exception as e:
                    self.log_issue("medium", module_name, "Error checking completion", e)
            
            self.log_test(f"Module {module_name}", "pass", 
                         f"Processed {question_count} questions")
            return True
            
        except Exception as e:
            self.log_issue("critical", module_name, "Exception during module test", e)
            self.log_test(f"Module {module_name}", "fail", f"Exception: {e}")
            traceback.print_exc()
            return False
    
    def test_demographics(self):
        """Test Demographics Module"""
        responses = [
            "34",
            "Male",
            "Bachelor's degree",
            "Software Engineer",
            "Single",
            "New York, USA",
            "Asian"
        ]
        return self.test_module_workflow("demographics", responses)
    
    def test_presenting_concern(self):
        """Test Presenting Concern Module"""
        responses = [
            "I've been feeling really anxious and depressed for the past few months",
            "It started about 3 months ago after I lost my job",
            "I feel anxious most days, especially in the morning",
            "It's affecting my sleep and ability to concentrate"
        ]
        return self.test_module_workflow("presenting_concern", responses)
    
    def test_risk_assessment(self):
        """Test Risk Assessment Module"""
        responses = [
            "No",
            "No",
            "No",
            "No",
            "No",
            "No"
        ]
        return self.test_module_workflow("risk_assessment", responses)
    
    def test_scid_screening(self):
        """Test SCID Screening Module"""
        responses = [
            "Yes",
            "Yes",
            "No",
            "Yes",
            "No"
        ]
        return self.test_module_workflow("scid_screening", responses)
    
    def test_scid_cv_diagnostic(self):
        """Test SCID-CV Diagnostic Module"""
        # This module may have variable questions based on selection
        responses = [
            "Yes",
            "Yes",
            "No",
            "Yes",
            "Sometimes",
            "No",
            "Yes"
        ]
        return self.test_module_workflow("scid_cv_diagnostic", responses)
    
    def test_da_diagnostic_analysis(self):
        """Test DA Diagnostic Analysis Module"""
        # DA should run automatically and may not require user input
        print("\n" + "="*80)
        print("TEST: DA Diagnostic Analysis")
        print("="*80)
        
        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_issue("critical", "da_diagnostic_analysis", "No session state")
                return False
            
            # DA should have been triggered automatically
            # Check if we're in DA module or if it completed
            if session_state.current_module == "da_diagnostic_analysis":
                # Process a dummy message to trigger DA
                result = self.moderator.process_message(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    message="continue"
                )
                print(f"  DA Response: {result[:200]}...")
                self.log_test("DA Diagnostic Analysis", "pass", "DA processed")
                return True
            else:
                # Check if DA already completed
                if "da_diagnostic_analysis" in session_state.module_history:
                    self.log_test("DA Diagnostic Analysis", "pass", "DA already completed")
                    return True
                else:
                    self.log_issue("medium", "da_diagnostic_analysis", 
                                 "DA not triggered automatically")
                    return False
                    
        except Exception as e:
            self.log_issue("high", "da_diagnostic_analysis", "Exception", e)
            traceback.print_exc()
            return False
    
    def test_tpa_treatment_planning(self):
        """Test TPA Treatment Planning Module"""
        # TPA should run automatically after DA
        print("\n" + "="*80)
        print("TEST: TPA Treatment Planning")
        print("="*80)
        
        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_issue("critical", "tpa_treatment_planning", "No session state")
                return False
            
            if session_state.current_module == "tpa_treatment_planning":
                result = self.moderator.process_message(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    message="continue"
                )
                print(f"  TPA Response: {result[:200]}...")
                self.log_test("TPA Treatment Planning", "pass", "TPA processed")
                return True
            elif "tpa_treatment_planning" in session_state.module_history:
                self.log_test("TPA Treatment Planning", "pass", "TPA already completed")
                return True
            else:
                self.log_issue("medium", "tpa_treatment_planning", 
                             "TPA not triggered automatically")
                return False
                
        except Exception as e:
            self.log_issue("high", "tpa_treatment_planning", "Exception", e)
            traceback.print_exc()
            return False
    
    def test_session_persistence(self):
        """Test session state persistence"""
        print("\n" + "="*80)
        print("TEST: Session Persistence")
        print("="*80)
        
        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_issue("high", "persistence", "Session state not found")
                return False
            
            # Check if data is stored
            if hasattr(self.moderator, 'db') and self.moderator.db:
                try:
                    db_session = self.moderator.db.get_session(self.session_id)
                    if db_session:
                        self.log_test("Session Persistence", "pass", "Session stored in database")
                    else:
                        self.log_issue("medium", "persistence", "Session not found in database")
                except Exception as e:
                    self.log_issue("medium", "persistence", "Database error", e)
            else:
                self.log_issue("low", "persistence", "Database not available")
            
            # Check module results
            if hasattr(session_state, 'module_results') and session_state.module_results:
                self.log_test("Module Results Storage", "pass", 
                            f"{len(session_state.module_results)} modules have results")
            else:
                self.log_issue("medium", "persistence", "No module results stored")
            
            return True
            
        except Exception as e:
            self.log_issue("high", "persistence", "Exception", e)
            return False
    
    def test_progress_tracking(self):
        """Test progress tracking"""
        print("\n" + "="*80)
        print("TEST: Progress Tracking")
        print("="*80)
        
        try:
            progress = self.moderator.get_session_progress(self.session_id)
            if not progress:
                self.log_issue("high", "progress", "No progress data")
                return False
            
            print(f"  Progress: {progress.get('overall_percentage', 0):.1f}%")
            print(f"  Current Module: {progress.get('current_module')}")
            print(f"  Completed Modules: {progress.get('completed_modules', [])}")
            print(f"  Total Modules: {progress.get('total_modules', 0)}")
            print(f"  Is Complete: {progress.get('is_complete', False)}")
            
            self.log_test("Progress Tracking", "pass", 
                         f"Progress: {progress.get('overall_percentage', 0):.1f}%")
            return True
            
        except Exception as e:
            self.log_issue("high", "progress", "Exception", e)
            return False
    
    def test_comprehensive_data_collection(self):
        """Test comprehensive data collection"""
        print("\n" + "="*80)
        print("TEST: Comprehensive Data Collection")
        print("="*80)
        
        try:
            data = self.moderator.collect_comprehensive_assessment_data(self.session_id)
            if not data:
                self.log_issue("high", "data_collection", "No comprehensive data")
                return False
            
            print(f"  Session ID: {data.get('session_id')}")
            print(f"  Module Results: {len(data.get('module_results', {}))} modules")
            print(f"  Module History: {data.get('module_history', [])}")
            print(f"  Current Module: {data.get('current_module')}")
            print(f"  Is Complete: {data.get('is_complete', False)}")
            
            self.log_test("Data Collection", "pass", 
                         f"Collected data from {len(data.get('module_results', {}))} modules")
            return True
            
        except Exception as e:
            self.log_issue("high", "data_collection", "Exception", e)
            return False
    
    def run_full_workflow_test(self):
        """Run the complete workflow test"""
        print("\n" + "="*80)
        print("COMPREHENSIVE ASSESSMENT WORKFLOW TEST")
        print("="*80)
        print(f"Started at: {datetime.now().isoformat()}")
        
        # Test initialization
        if not self.test_initialization():
            print("\n❌ Initialization failed - cannot continue")
            return
        
        # Test starting assessment
        if not self.test_start_assessment():
            print("\n❌ Start assessment failed - cannot continue")
            return
        
        # Test each module in sequence
        module_tests = [
            ("Demographics", self.test_demographics),
            ("Presenting Concern", self.test_presenting_concern),
            ("Risk Assessment", self.test_risk_assessment),
            ("SCID Screening", self.test_scid_screening),
            ("SCID-CV Diagnostic", self.test_scid_cv_diagnostic),
            ("DA Diagnostic Analysis", self.test_da_diagnostic_analysis),
            ("TPA Treatment Planning", self.test_tpa_treatment_planning),
        ]
        
        for test_name, test_func in module_tests:
            try:
                test_func()
            except Exception as e:
                self.log_issue("critical", test_name.lower().replace(" ", "_"), 
                             f"Unhandled exception in {test_name}", e)
                traceback.print_exc()
        
        # Test additional features
        self.test_session_persistence()
        self.test_progress_tracking()
        self.test_comprehensive_data_collection()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and issues"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        # Test results summary
        passed = sum(1 for r in self.test_results if r["status"] == "pass")
        failed = sum(1 for r in self.test_results if r["status"] == "fail")
        warnings = sum(1 for r in self.test_results if r["status"] == "warning")
        
        print(f"\nTest Results: {passed} passed, {failed} failed, {warnings} warnings")
        
        # Issues summary
        print(f"\nIssues Found: {len(self.issues)}")
        critical = [i for i in self.issues if i["severity"] == "critical"]
        high = [i for i in self.issues if i["severity"] == "high"]
        medium = [i for i in self.issues if i["severity"] == "medium"]
        low = [i for i in self.issues if i["severity"] == "low"]
        
        print(f"  Critical: {len(critical)}")
        print(f"  High: {len(high)}")
        print(f"  Medium: {len(medium)}")
        print(f"  Low: {len(low)}")
        
        # Print all issues grouped by severity
        if critical:
            print("\n" + "="*80)
            print("CRITICAL ISSUES")
            print("="*80)
            for issue in critical:
                print(f"\n[{issue['module']}] {issue['description']}")
                if issue['error']:
                    print(f"  Error: {issue['error']}")
        
        if high:
            print("\n" + "="*80)
            print("HIGH PRIORITY ISSUES")
            print("="*80)
            for issue in high:
                print(f"\n[{issue['module']}] {issue['description']}")
                if issue['error']:
                    print(f"  Error: {issue['error']}")
        
        if medium:
            print("\n" + "="*80)
            print("MEDIUM PRIORITY ISSUES")
            print("="*80)
            for issue in medium[:10]:  # Show first 10
                print(f"\n[{issue['module']}] {issue['description']}")
                if issue['error']:
                    print(f"  Error: {issue['error']}")
            if len(medium) > 10:
                print(f"\n... and {len(medium) - 10} more medium priority issues")
        
        # Print failed tests
        if failed > 0:
            print("\n" + "="*80)
            print("FAILED TESTS")
            print("="*80)
            for result in self.test_results:
                if result["status"] == "fail":
                    print(f"\n{result['step']}: {result['details']}")
        
        print("\n" + "="*80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        print("="*80)


if __name__ == "__main__":
    tester = WorkflowTester()
    tester.run_full_workflow_test()

