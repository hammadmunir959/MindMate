import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.diagnosis.agent_v2 import evaluate_disorder_criteria

def test_scoring_logic():
    print("🧪 Testing Diagnosis Scoring Logic (V2.1)")
    print("=======================================")

    # Mock Symptoms for MDD
    # Required: MDD_A1 (Depressed Mood), MDD_A2 (Loss of interest)
    # Supporting: MDD_A3 (Weight), MDD_A4 (Sleep), MDD_A5 (Agitation), MDD_A6 (Fatigue), etc.

    # CASE 1: Full Blown MDD (High Confidence)
    symptoms_1 = [
        {"name": "Depressed mood", "dsm_criteria_id": "MDD_A1", "severity": 0.8},
        {"name": "Loss of interest", "dsm_criteria_id": "MDD_A2", "severity": 0.9},
        {"name": "Insomnia", "dsm_criteria_id": "MDD_A4", "severity": 0.7},
        {"name": "Fatigue", "dsm_criteria_id": "MDD_A6", "severity": 0.6},
        {"name": "Guilt", "dsm_criteria_id": "MDD_A7", "severity": 0.6},
    ]
    
    result_1 = evaluate_disorder_criteria("MDD", symptoms_1)
    print(f"\n[Case 1] Full MDD (2 Core + 3 Supp)")
    print(f"  Confidence: {result_1['confidence']} (Expected > 0.8)")
    print(f"  Status: {result_1['severity']}")
    print(f"  Met: {result_1['diagnosis_met']}")
    
    # CASE 2: Sub-threshold (1 Core, but enough supporting) -> "Other Specified" logic maybe?
    # Current logic: needs 5 total. Let's give 1 core + 4 supporting.
    symptoms_2 = [
        {"name": "Depressed mood", "dsm_criteria_id": "MDD_A1", "severity": 0.6},
        {"name": "Insomnia", "dsm_criteria_id": "MDD_A4", "severity": 0.5},
        {"name": "Fatigue", "dsm_criteria_id": "MDD_A6", "severity": 0.5},
        {"name": "Guilt", "dsm_criteria_id": "MDD_A7", "severity": 0.5},
        {"name": "Concentration", "dsm_criteria_id": "MDD_A8", "severity": 0.5},
    ]
    
    result_2 = evaluate_disorder_criteria("MDD", symptoms_2)
    print(f"\n[Case 2] Sub-threshold (1 Core + 4 Supp)")
    print(f"  Confidence: {result_2['confidence']} (Expected ~0.5-0.7)")
    print(f"  Met: {result_2['diagnosis_met']}")
    
    # CASE 3: No Core Symptoms (Should be heavily penalized)
    symptoms_3 = [
        {"name": "Insomnia", "dsm_criteria_id": "MDD_A4", "severity": 0.5},
        {"name": "Fatigue", "dsm_criteria_id": "MDD_A6", "severity": 0.5},
        {"name": "Guilt", "dsm_criteria_id": "MDD_A7", "severity": 0.5},
    ]
    
    result_3 = evaluate_disorder_criteria("MDD", symptoms_3)
    print(f"\n[Case 3] No Core Symptoms (Only Supporting)")
    print(f"  Confidence: {result_3['confidence']} (Expected < 0.3 due to penalty)")
    print(f"  Met: {result_3['diagnosis_met']}")

if __name__ == "__main__":
    test_scoring_logic()
