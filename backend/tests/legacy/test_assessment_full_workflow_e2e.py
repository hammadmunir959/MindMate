"""
Comprehensive End-to-End Assessment Workflow Test
=================================================
Tests the complete assessment workflow from start to finish:
1. Start assessment session
2. Complete all modules in sequence
3. Verify data collection and storage
4. Test progress tracking
5. Verify final results and reports
6. Test API endpoints integration

This test simulates a real user journey through the entire assessment system.
Supports running with real patient data by providing --patient-id or
--patient-email so that database persistence behaves like production.
"""

import argparse
import sys
import os
import traceback
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.assessment.assessment_v2.moderator import AssessmentModerator
from app.agents.assessment.assessment_v2.config import get_module_sequence

try:
    from app.db.session import SessionLocal
    from app.models.patient import Patient
except Exception:  # pragma: no cover - optional DB import for CLI lookup
    SessionLocal = None
    Patient = None


def normalize_patient_id(patient_id: Optional[str]) -> Optional[str]:
    """Validate and normalize patient UUID strings."""
    if not patient_id:
        return None
    try:
        return str(uuid.UUID(str(patient_id)))
    except ValueError as exc:
        raise ValueError(f"Invalid patient UUID provided: {patient_id}") from exc


def resolve_patient_identifier(
    patient_id: Optional[str],
    patient_email: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve patient UUID (and default user_id) from CLI arguments."""
    if patient_id:
        normalized = normalize_patient_id(patient_id)
        return normalized, None

    if patient_email and SessionLocal and Patient:
        db = SessionLocal()
        try:
            patient = db.query(Patient).filter(Patient.email == patient_email).first()
            if not patient:
                raise ValueError(f"No patient found with email: {patient_email}")
            return str(patient.id), patient.email
        finally:
            db.close()

    return None, None


class FullWorkflowE2ETester:
    """Comprehensive end-to-end workflow tester"""

    def __init__(
        self,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        preset_session_id: Optional[str] = None
    ):
        self.moderator: Optional[AssessmentModerator] = None
        self.session_id: Optional[str] = None
        self.user_id = user_id or f"test_user_{uuid.uuid4().hex[:8]}"
        self.patient_id = patient_id
        self._preset_session_id = preset_session_id
        self.test_results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.module_responses: Dict[str, List[str]] = {}
        self.current_module: Optional[str] = None
        self.completed_modules: List[str] = []
        self.session_persisted: bool = False

    def log_result(self, step: str, status: str, details: str = "", data: Any = None):
        """Log a test result"""
        result = {
            "step": step,
            "status": status,  # "pass", "fail", "warning", "skip"
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        status_icon = {
            "pass": "✅",
            "fail": "❌",
            "warning": "⚠️",
            "skip": "⏭️"
        }.get(status, "❓")

        print(f"{status_icon} [{step}] {details}")
        if data and isinstance(data, dict):
            for key, value in list(data.items())[:3]:  # Show first 3 items
                print(f"      {key}: {value}")

    def log_error(self, step: str, error: Exception, context: str = ""):
        """Log an error"""
        error_info = {
            "step": step,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_info)
        print(f"❌ ERROR in [{step}]: {error}")
        if context:
            print(f"   Context: {context}")

    def test_initialization(self) -> bool:
        """Test 1: Initialize AssessmentModerator"""
        print("\n" + "="*80)
        print("STEP 1: Initialize Assessment System")
        print("="*80)

        try:
            self.moderator = AssessmentModerator()

            if not self.moderator:
                self.log_result("Initialization", "fail", "Moderator is None")
                return False

            if len(self.moderator.modules) == 0:
                self.log_result("Initialization", "fail", "No modules loaded")
                return False

            module_names = list(self.moderator.modules.keys())
            self.log_result(
                "Initialization",
                "pass",
                f"Loaded {len(module_names)} modules",
                {"modules": module_names[:5]}  # Show first 5
            )
            return True

        except Exception as e:
            self.log_error("Initialization", e)
            self.log_result("Initialization", "fail", f"Exception: {e}")
            traceback.print_exc()
            return False

    def test_start_assessment(self) -> bool:
        """Test 2: Start Assessment Session"""
        print("\n" + "="*80)
        print("STEP 2: Start Assessment Session")
        print("="*80)

        try:
            if self._preset_session_id:
                self.session_id = self._preset_session_id
            else:
                self.session_id = f"test_e2e_{uuid.uuid4().hex[:8]}"

            greeting = self.moderator.start_assessment(
                user_id=self.user_id,
                session_id=self.session_id
            )

            if not greeting:
                self.log_result("Start Assessment", "fail", "No greeting returned")
                return False

            if len(greeting.strip()) < 10:
                self.log_result("Start Assessment", "warning", f"Very short greeting: '{greeting}'")

            # Check session state
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_result("Start Assessment", "fail", "Session state not created")
                return False

            self.current_module = session_state.current_module
            if not self.current_module:
                self.log_result("Start Assessment", "fail", "No current module set")
                return False

            expected_start = get_module_sequence()[0] if get_module_sequence() else None
            if expected_start and self.current_module != expected_start:
                self.log_result(
                    "Start Assessment",
                    "warning",
                    f"Starting module mismatch: expected '{expected_start}', got '{self.current_module}'"
                )

            # Attach patient metadata for real data runs
            if self.patient_id:
                self.attach_patient_to_session()

            self.log_result(
                "Start Assessment",
                "pass",
                "Session started successfully",
                {
                    "session_id": self.session_id,
                    "current_module": self.current_module,
                    "greeting_preview": greeting[:100] + "..." if len(greeting) > 100 else greeting
                }
            )
            return True

        except Exception as e:
            self.log_error("Start Assessment", e)
            self.log_result("Start Assessment", "fail", f"Exception: {e}")
            traceback.print_exc()
            return False

    def process_module_interaction(
        self,
        module_name: str,
        responses: List[str],
        max_iterations: int = 30
    ) -> bool:
        """Process interactions with a module until completion."""
        print(f"\n  Processing module: {module_name}")
        print(f"  Available responses: {len(responses)}")

        question_count = 0
        response_index = 0

        try:
            while question_count < max_iterations:
                session_state = self.moderator.get_session_state(self.session_id)
                if not session_state:
                    self.log_result(f"{module_name} - Session Check", "fail", "Session state lost")
                    return False

                if session_state.current_module != module_name:
                    print(f"  ✓ Module '{module_name}' completed! Moved to: {session_state.current_module}")
                    self.completed_modules.append(module_name)
                    self.current_module = session_state.current_module
                    self.log_result(
                        f"{module_name} - Completion",
                        "pass",
                        f"Completed after {question_count} questions"
                    )
                    return True

                if response_index >= len(responses):
                    response_index = 0

                response_text = responses[response_index]
                response_index += 1

                print(f"    Q{question_count + 1}: Sending: '{response_text[:50]}...'")

                try:
                    result = self.moderator.process_message(
                        user_id=self.user_id,
                        session_id=self.session_id,
                        message=response_text
                    )

                    if not result:
                        self.log_result(
                            f"{module_name} - Response {question_count + 1}",
                            "fail",
                            "Empty response"
                        )
                        return False

                    if len(result.strip()) < 5:
                        self.log_result(
                            f"{module_name} - Response {question_count + 1}",
                            "warning",
                            f"Very short response: '{result}'"
                        )

                    question_count += 1

                    session_state = self.moderator.get_session_state(self.session_id)
                    if session_state and session_state.current_module != module_name:
                        print(f"  ✓ Module '{module_name}' completed! Moved to: {session_state.current_module}")
                        self.completed_modules.append(module_name)
                        self.current_module = session_state.current_module
                        self.log_result(
                            f"{module_name} - Completion",
                            "pass",
                            f"Completed after {question_count} questions"
                        )
                        return True

                except Exception as e:
                    self.log_error(f"{module_name} - Process Message", e, f"Question {question_count + 1}")
                    question_count += 1
                    continue

            session_state = self.moderator.get_session_state(self.session_id)
            if session_state and session_state.current_module == module_name:
                self.log_result(
                    f"{module_name} - Max Iterations",
                    "warning",
                    f"Reached max iterations ({max_iterations}) without completion"
                )
                if self.patient_id:
                    self.attach_patient_to_session(log_warnings=False)
                return False

            self.completed_modules.append(module_name)
            self.log_result(
                f"{module_name} - Completion",
                "pass",
                f"Completed after {question_count} questions"
            )
            return True

        except Exception as e:
            self.log_error(f"{module_name} - Module Processing", e)
            return False

    def test_demographics_module(self) -> bool:
        """Test Demographics Module"""
        print("\n" + "="*80)
        print("STEP 3: Demographics Module")
        print("="*80)

        responses = [
            "34",
            "Male",
            "Bachelor's degree",
            "Software Engineer",
            "Single",
            "New York, USA",
            "Asian",
            "Living with family",
            "Stable",
            "Work stress, financial concerns"
        ]

        return self.process_module_interaction("demographics", responses)

    def test_presenting_concern_module(self) -> bool:
        """Test Presenting Concern Module"""
        print("\n" + "="*80)
        print("STEP 4: Presenting Concern Module")
        print("="*80)

        responses = [
            "I've been feeling really anxious and depressed for the past few months",
            "It started about 3 months ago after I lost my job",
            "I feel anxious most days, especially in the morning",
            "It's affecting my sleep and ability to concentrate at work",
            "I have trouble falling asleep and wake up feeling tired",
            "I've lost interest in activities I used to enjoy",
            "I feel hopeless about the future sometimes"
        ]

        return self.process_module_interaction("presenting_concern", responses)

    def test_risk_assessment_module(self) -> bool:
        """Test Risk Assessment Module"""
        print("\n" + "="*80)
        print("STEP 5: Risk Assessment Module")
        print("="*80)

        responses = [
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No"
        ]

        return self.process_module_interaction("risk_assessment", responses)

    def test_scid_screening_module(self) -> bool:
        """Test SCID Screening Module"""
        print("\n" + "="*80)
        print("STEP 6: SCID Screening Module")
        print("="*80)

        responses = [
            "Yes",
            "Yes",
            "No",
            "Yes",
            "Sometimes",
            "No",
            "Yes",
            "No"
        ]

        return self.process_module_interaction("scid_screening", responses)

    def test_scid_cv_diagnostic_module(self) -> bool:
        """Test SCID-CV Diagnostic Module"""
        print("\n" + "="*80)
        print("STEP 7: SCID-CV Diagnostic Module")
        print("="*80)

        responses = [
            "Yes",
            "Yes",
            "No",
            "Yes",
            "Sometimes",
            "No",
            "Yes",
            "Moderate",
            "No",
            "Yes"
        ]

        return self.process_module_interaction("scid_cv_diagnostic", responses)

    def test_da_diagnostic_analysis_module(self) -> bool:
        """Test DA Diagnostic Analysis Module (auto-triggered)"""
        print("\n" + "="*80)
        print("STEP 8: DA Diagnostic Analysis Module")
        print("="*80)

        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_result("DA Module", "fail", "No session state")
                return False

            if session_state.current_module == "da_diagnostic_analysis":
                result = self.moderator.process_message(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    message="continue"
                )

                self.log_result(
                    "DA Module",
                    "pass",
                    "DA processed successfully",
                    {"response_preview": result[:200] + "..." if len(result) > 200 else result}
                )
                return True
            elif "da_diagnostic_analysis" in session_state.module_history:
                self.log_result("DA Module", "pass", "DA already completed")
                return True

            result = self.moderator.process_message(
                user_id=self.user_id,
                session_id=self.session_id,
                message="continue"
            )

            session_state = self.moderator.get_session_state(self.session_id)
            if "da_diagnostic_analysis" in session_state.module_history:
                self.log_result("DA Module", "pass", "DA triggered and completed")
                return True

            self.log_result("DA Module", "warning", "DA not automatically triggered")
            return False

        except Exception as e:
            self.log_error("DA Module", e)
            return False

    def test_tpa_treatment_planning_module(self) -> bool:
        """Test TPA Treatment Planning Module (auto-triggered after DA)"""
        print("\n" + "="*80)
        print("STEP 9: TPA Treatment Planning Module")
        print("="*80)

        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_result("TPA Module", "fail", "No session state")
                return False

            if session_state.current_module == "tpa_treatment_planning":
                result = self.moderator.process_message(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    message="continue"
                )

                self.log_result(
                    "TPA Module",
                    "pass",
                    "TPA processed successfully",
                    {"response_preview": result[:200] + "..." if len(result) > 200 else result}
                )
                return True
            elif "tpa_treatment_planning" in session_state.module_history:
                self.log_result("TPA Module", "pass", "TPA already completed")
                return True

            result = self.moderator.process_message(
                user_id=self.user_id,
                session_id=self.session_id,
                message="continue"
            )

            session_state = self.moderator.get_session_state(self.session_id)
            if "tpa_treatment_planning" in session_state.module_history:
                self.log_result("TPA Module", "pass", "TPA triggered and completed")
                return True

            self.log_result("TPA Module", "warning", "TPA not automatically triggered")
            return False

        except Exception as e:
            self.log_error("TPA Module", e)
            return False

    def test_progress_tracking(self) -> bool:
        """Test progress tracking throughout workflow"""
        print("\n" + "="*80)
        print("STEP 10: Progress Tracking Verification")
        print("="*80)

        try:
            progress = self.moderator.get_session_progress(self.session_id)
            if not progress:
                self.log_result("Progress Tracking", "fail", "No progress data")
                return False

            progress_pct = progress.get('overall_percentage') or progress.get('overall', 0)
            current_module = progress.get('current_module')
            completed_modules = progress.get('completed_modules', [])
            total_modules = progress.get('total_modules', 0)
            is_complete = progress.get('is_complete', False)

            self.log_result(
                "Progress Tracking",
                "pass",
                f"Progress: {progress_pct:.1f}%",
                {
                    "current_module": current_module,
                    "completed_modules": len(completed_modules),
                    "total_modules": total_modules,
                    "is_complete": is_complete
                }
            )
            return True

        except Exception as e:
            self.log_error("Progress Tracking", e)
            return False

    def test_data_collection(self) -> bool:
        """Test comprehensive data collection"""
        print("\n" + "="*80)
        print("STEP 11: Comprehensive Data Collection")
        print("="*80)

        try:
            data = self.moderator.collect_comprehensive_assessment_data(self.session_id)
            if not data:
                self.log_result("Data Collection", "fail", "No comprehensive data")
                return False

            module_results = data.get('module_results', {})
            module_history = data.get('module_history', [])

            self.log_result(
                "Data Collection",
                "pass",
                f"Collected data from {len(module_results)} modules",
                {
                    "module_results_count": len(module_results),
                    "module_history": module_history,
                    "session_id": data.get('session_id'),
                    "is_complete": data.get('is_complete', False)
                }
            )
            return True

        except Exception as e:
            self.log_error("Data Collection", e)
            return False

    def test_comprehensive_report(self) -> bool:
        """Test comprehensive report generation"""
        print("\n" + "="*80)
        print("STEP 12: Comprehensive Report Generation")
        print("="*80)

        try:
            report = self.moderator.generate_comprehensive_report(self.session_id)
            if not report:
                self.log_result("Comprehensive Report", "fail", "No report generated")
                return False

            self.log_result(
                "Comprehensive Report",
                "pass",
                f"Report generated ({len(report)} characters)",
                {"report_preview": report[:300] + "..." if len(report) > 300 else report}
            )
            return True

        except Exception as e:
            self.log_error("Comprehensive Report", e)
            return False

    def test_session_persistence(self) -> bool:
        """Test session persistence and database storage"""
        print("\n" + "="*80)
        print("STEP 13: Session Persistence & Database Storage")
        print("="*80)

        try:
            session_state = self.moderator.get_session_state(self.session_id)
            if not session_state:
                self.log_result("Session Persistence", "fail", "Session state not found")
                return False

            if hasattr(self.moderator, 'db') and self.moderator.db:
                try:
                    db_session = self.moderator.db.get_session(self.session_id)
                    if db_session:
                        self.log_result("Session Persistence", "pass", "Session stored in database")
                    else:
                        self.log_result("Session Persistence", "warning", "Session not found in database")
                except Exception as e:
                    self.log_result("Session Persistence", "warning", f"Database check error: {e}")
            else:
                self.log_result("Session Persistence", "skip", "Database not available")

            if hasattr(session_state, 'module_results') and session_state.module_results:
                self.log_result(
                    "Module Results Storage",
                    "pass",
                    f"{len(session_state.module_results)} modules have results stored"
                )
            else:
                self.log_result("Module Results Storage", "warning", "No module results stored")

            return True

        except Exception as e:
            self.log_error("Session Persistence", e)
            return False

    def run_full_workflow_test(self):
        """Run the complete end-to-end workflow test"""
        print("\n" + "="*80)
        print("COMPREHENSIVE END-TO-END ASSESSMENT WORKFLOW TEST")
        print("="*80)
        print(f"Started at: {datetime.now().isoformat()}")
        print(f"User ID: {self.user_id}")
        if self.patient_id:
            print(f"Patient ID: {self.patient_id}")
        print("="*80)

        if not self.test_initialization():
            print("\n❌ Initialization failed - cannot continue")
            self.print_summary()
            return

        if not self.test_start_assessment():
            print("\n❌ Start assessment failed - cannot continue")
            self.print_summary()
            return

        module_tests = [
            ("Demographics", self.test_demographics_module),
            ("Presenting Concern", self.test_presenting_concern_module),
            ("Risk Assessment", self.test_risk_assessment_module),
            ("SCID Screening", self.test_scid_screening_module),
            ("SCID-CV Diagnostic", self.test_scid_cv_diagnostic_module),
            ("DA Diagnostic Analysis", self.test_da_diagnostic_analysis_module),
            ("TPA Treatment Planning", self.test_tpa_treatment_planning_module),
        ]

        for test_name, test_func in module_tests:
            try:
                test_func()
            except Exception as e:
                self.log_error(test_name, e, "Unhandled exception")
                traceback.print_exc()

        self.test_progress_tracking()
        self.test_data_collection()
        self.test_comprehensive_report()
        self.test_session_persistence()

        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        passed = sum(1 for r in self.test_results if r["status"] == "pass")
        failed = sum(1 for r in self.test_results if r["status"] == "fail")
        warnings = sum(1 for r in self.test_results if r["status"] == "warning")
        skipped = sum(1 for r in self.test_results if r["status"] == "skip")

        print(f"\nTest Results:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        print(f"  ⏭️  Skipped: {skipped}")
        print(f"  📊 Total: {len(self.test_results)}")

        if self.errors:
            print(f"\nErrors Found: {len(self.errors)}")
            for error in self.errors[:5]:
                print(f"  ❌ [{error['step']}] {error['error_type']}: {error['error_message']}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")

        print(f"\nModule Completion:")
        print(f"  Completed: {len(self.completed_modules)}")
        print(f"  Modules: {', '.join(self.completed_modules)}")
        print(f"  Current: {self.current_module}")

        print(f"\nSession Information:")
        print(f"  Session ID: {self.session_id}")
        print(f"  User ID: {self.user_id}")
        if self.patient_id:
            print(f"  Patient ID: {self.patient_id}")

        if failed > 0:
            print("\n" + "="*80)
            print("FAILED TESTS")
            print("="*80)
            for result in self.test_results:
                if result["status"] == "fail":
                    print(f"\n❌ {result['step']}: {result['details']}")
                    if result.get("data"):
                        print(f"   Data: {result['data']}")

        if warnings > 0:
            print("\n" + "="*80)
            print("WARNINGS")
            print("="*80)
            for result in self.test_results[:10]:
                if result["status"] == "warning":
                    print(f"\n⚠️  {result['step']}: {result['details']}")

        print("\n" + "="*80)
        print(f"Test completed at: {datetime.now().isoformat()}")
        print("="*80)

    def attach_patient_to_session(self, log_warnings: bool = True):
        """Attach patient metadata to session and ensure DB persistence."""
        if not self.patient_id or not self.session_id:
            return

        session_state = self.moderator.get_session_state(self.session_id)
        if not session_state:
            return

        if not getattr(session_state, "metadata", None):
            session_state.metadata = {}
        session_state.metadata["patient_id"] = self.patient_id

        if hasattr(self.moderator, "db") and self.moderator.db:
            try:
                db_session = self.moderator.db.get_session(self.session_id)
                if not db_session:
                    self.moderator.db.create_session(session_state, self.patient_id)
                self.session_persisted = True
            except Exception as exc:
                if log_warnings:
                    self.log_result(
                        "Attach Patient",
                        "warning",
                        f"Failed to persist session with patient_id: {exc}"
                    )
        elif log_warnings:
            self.log_result(
                "Attach Patient",
                "warning",
                "Moderator database interface not available; session metadata updated only"
            )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run full assessment workflow E2E test.")
    parser.add_argument(
        "--user-id",
        help="Identifier used for AssessmentModerator interactions (defaults to generated test ID or patient email)."
    )
    parser.add_argument(
        "--patient-id",
        help="Patient UUID to associate with the session (ensures DB persistence)."
    )
    parser.add_argument(
        "--patient-email",
        help="Patient email to look up UUID from the database (requires DB access)."
    )
    parser.add_argument(
        "--session-id",
        help="Provide an existing session ID to reuse; otherwise a new one is generated."
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()

    patient_id, default_user_id = resolve_patient_identifier(
        cli_args.patient_id,
        cli_args.patient_email
    )

    user_id = cli_args.user_id or default_user_id
    if patient_id and not user_id:
        user_id = f"patient_{patient_id}"

    tester = FullWorkflowE2ETester(
        user_id=user_id,
        patient_id=patient_id,
        preset_session_id=cli_args.session_id
    )
    tester.run_full_workflow_test()


