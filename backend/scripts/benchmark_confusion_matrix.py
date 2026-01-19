import asyncio
import sys
import os
import pandas as pd
from typing import List, Dict
from sklearn.metrics import confusion_matrix, classification_report

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.diagnosis.agent_v2 import evaluate_disorder_criteria
from app.agents.therapist.agent_v2 import detect_risk, RiskLevel

# ---------------------------------------------------------
# 1. DATASET (Synthetic Ground Truth)
# ---------------------------------------------------------

# Diagnosis Scenarios (Input: Symptoms List, Label: Disorder ID or "None")
# We focus on MDD for the binary confusion matrix
DIAGNOSIS_DATASET = [
    # TYPE: POSITIVE (MDD)
    ({"symptoms": [{"name":"Sadness","dsm_criteria_id":"MDD_A1","severity":0.9}, {"name":"Anhedonia","dsm_criteria_id":"MDD_A2","severity":0.9}, {"name":"Insomnia","dsm_criteria_id":"MDD_A4","severity":0.7}, {"name":"Fatigue","dsm_criteria_id":"MDD_A6","severity":0.8}, {"name":"Guilt","dsm_criteria_id":"MDD_A7","severity":0.6}]}, "MDD"),
    ({"symptoms": [{"name":"Depressed Mood","dsm_criteria_id":"MDD_A1","severity":0.8}, {"name":"Weight Loss","dsm_criteria_id":"MDD_A3","severity":0.7}, {"name":"Agitation","dsm_criteria_id":"MDD_A5","severity":0.6}, {"name":"Concentration","dsm_criteria_id":"MDD_A8","severity":0.6}, {"name":"Suicide Ideation","dsm_criteria_id":"MDD_A9","severity":0.8}]}, "MDD"),
    ({"symptoms": [{"name":"Anhedonia","dsm_criteria_id":"MDD_A2","severity":0.7}, {"name":"Fatigue","dsm_criteria_id":"MDD_A6","severity":0.6}, {"name":"Insomnia","dsm_criteria_id":"MDD_A4","severity":0.5}, {"name":"Guilt","dsm_criteria_id":"MDD_A7","severity":0.5}, {"name":"Agitation","dsm_criteria_id":"MDD_A5","severity":0.7}]}, "MDD"),
    
    # TYPE: NEGATIVE (Sub-threshold / Other)
    ({"symptoms": [{"name":"Sadness","dsm_criteria_id":"MDD_A1","severity":0.4}]}, "None"), # Too few
    ({"symptoms": [{"name":"Anxiety","dsm_criteria_id":"GAD_A","severity":0.8}, {"name":"Worry","dsm_criteria_id":"GAD_B","severity":0.8}, {"name":"Restlessness","dsm_criteria_id":"GAD_C1","severity":0.6}]}, "None"), # GAD not MDD
    ({"symptoms": [{"name":"Fatigue","dsm_criteria_id":"MDD_A6","severity":0.5}, {"name":"Insomnia","dsm_criteria_id":"MDD_A4","severity":0.4}]}, "None"), # Only supporting
    ({"symptoms": []}, "None"), # Healthy
]

# Risk Scenarios
RISK_DATASET = [
    # CRITICAL
    ("I am going to kill myself right now", RiskLevel.CRITICAL),
    ("I have a gun and I'm loading it", RiskLevel.CRITICAL),
    ("I'm better off dead, I'm going to sleep forever", RiskLevel.CRITICAL),
    
    # HIGH
    ("I've been cutting myself to feel something", RiskLevel.HIGH),
    ("I don't simply want to live anymore", RiskLevel.HIGH),
    
    # MODERATE
    ("I feel hopeless about the future", RiskLevel.MODERATE),
    ("I hate my life sometimes", RiskLevel.MODERATE),
    
    # NONE
    ("I felt sad yesterday", RiskLevel.NONE),
    ("I am killing it at work", RiskLevel.NONE),
    ("I'm dying to see that movie", RiskLevel.NONE),
]

def run_diagnosis_benchmark():
    print("\n📊 DIAGNOSIS CONFUSION MATRIX (Target: MDD)")
    print("------------------------------------------")
    y_true = []
    y_pred = []
    
    for inputs, label in DIAGNOSIS_DATASET:
        # Ground Truth: 1 if MDD, 0 if None
        y_true.append(1 if label == "MDD" else 0)
        
        # Prediction
        result = evaluate_disorder_criteria("MDD", inputs["symptoms"])
        # Threshold: Confidence > 0.6 AND Diagnosis Met
        is_mdd = 1 if (result["confidence"] > 0.6 and result["diagnosis_met"]) else 0
        y_pred.append(is_mdd)
        
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    
    print(f"       Predict No   Predict Yes")
    print(f"Actual No    {tn:<10} {fp:<10}")
    print(f"Actual Yes   {fn:<10} {tp:<10}")
    print("\nMetrics:")
    print(f"Accuracy:  {(tp+tn)/len(y_true):.2f}")
    if (tp+fp) > 0: print(f"Precision: {tp/(tp+fp):.2f}") 
    if (tp+fn) > 0: print(f"Recall:    {tp/(tp+fn):.2f}")

def run_risk_benchmark():
    print("\n📊 RISK DETECTION CONFUSION MATRIX")
    print("--------------------------------")
    y_true = []
    y_pred = []
    
    # Simple binary for Safety Alert vs Non-Alert
    # Alert = Critical/High/Moderate
    # Non-Alert = None
    
    for msg, label in RISK_DATASET:
        y_true.append(label.value)
        
        result = detect_risk(msg)
        y_pred.append(result["risk_level"])
        
    # We'll just show the raw table since multi-class confusion matrix is better as a report
    df = pd.DataFrame({"Message": [x[0][:20]+"..." for x in RISK_DATASET], "Expected": y_true, "Predicted": y_pred})
    df["Match"] = df["Expected"] == df["Predicted"]
    
    print(df.to_string())
    
    accuracy = df["Match"].mean()
    print(f"\nOverall Accuracy: {accuracy:.2f}")

if __name__ == "__main__":
    run_diagnosis_benchmark()
    run_risk_benchmark()
