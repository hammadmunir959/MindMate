"""
MCP Tool: Generate Report
=========================
Generates clinical report with severity and recommendations.
"""

from typing import Dict, List, Any
from datetime import datetime


TOOL_SCHEMA = {
    "name": "generate_report",
    "description": "Generate clinical report with diagnoses, severity, and recommendations",
    "inputSchema": {
        "type": "object",
        "properties": {
            "diagnoses": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of confirmed diagnoses"
            },
            "symptoms": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["diagnoses", "symptoms"]
    }
}


async def execute(
    diagnoses: List[Dict],
    symptoms: List[Dict],
    llm_client = None
) -> Dict[str, Any]:
    """
    Generate clinical summary report.
    
    Returns:
        - report: str (clinical summary)
        - primary_diagnosis: dict
        - recommendations: list
    """
    if not diagnoses:
        return {
            "report": "Based on the assessment, no specific mental health conditions met the diagnostic criteria at this time. The patient may benefit from general wellness support and follow-up.",
            "primary_diagnosis": None,
            "recommendations": [
                "Continue monitoring symptoms",
                "Schedule follow-up assessment in 2-4 weeks",
                "Consider general mental wellness practices"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    # Sort by confidence to get primary
    sorted_diagnoses = sorted(diagnoses, key=lambda d: d.get("confidence", 0), reverse=True)
    primary = sorted_diagnoses[0]
    
    # Mark primary
    for i, d in enumerate(sorted_diagnoses):
        d["is_primary"] = (i == 0)
    
    # Generate report
    symptom_summary = ", ".join([s.get("name", "") for s in symptoms[:5]])
    
    if llm_client:
        try:
            diag_text = "\n".join([
                f"- {d['disorder_name']} (confidence: {d.get('confidence', 0):.0%}, severity: {d.get('severity', 'moderate')})"
                for d in sorted_diagnoses
            ])
            
            prompt = f"""Generate a brief clinical summary report.

Diagnoses:
{diag_text}

Key Symptoms: {symptom_summary}

Write a 2-3 sentence professional clinical summary and 3 specific recommendations.
Return JSON: {{"summary": "...", "recommendations": ["...", "...", "..."]}}
"""
            response = await llm_client.generate_async(
                prompt=prompt,
                system_prompt="You are a clinical report writer. Be professional and concise.",
                temperature=0.3,
                max_tokens=300
            )
            
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "report": result.get("summary", ""),
                    "primary_diagnosis": primary,
                    "all_diagnoses": sorted_diagnoses,
                    "recommendations": result.get("recommendations", []),
                    "generated_at": datetime.utcnow().isoformat()
                }
        except Exception:
            pass
    
    # Fallback: Template-based report
    primary_name = primary.get("disorder_name", "Unknown")
    severity = primary.get("severity", "moderate")
    
    report = (
        f"Clinical Assessment Summary: The patient presents with symptoms consistent "
        f"with {primary_name} ({severity} severity). "
        f"Key presenting symptoms include {symptom_summary}. "
        f"The assessment indicates a need for professional mental health support."
    )
    
    # Generate recommendations based on diagnosis
    recommendations = _get_recommendations(primary.get("disorder_id", ""), severity)
    
    return {
        "report": report,
        "primary_diagnosis": primary,
        "all_diagnoses": sorted_diagnoses,
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat()
    }


def _get_recommendations(disorder_id: str, severity: str) -> List[str]:
    """Get treatment recommendations based on disorder."""
    base_recs = {
        "MDD": [
            "Consider Cognitive Behavioral Therapy (CBT)",
            "Discuss antidepressant options with a psychiatrist",
            "Establish regular sleep and exercise routines"
        ],
        "GAD": [
            "Consider anxiety-focused therapy (CBT or ACT)",
            "Practice relaxation techniques and mindfulness",
            "Limit caffeine and stimulant intake"
        ],
        "PANIC": [
            "Learn panic attack management techniques",
            "Consider exposure therapy with a specialist",
            "Rule out cardiac conditions with medical evaluation"
        ],
        "PTSD": [
            "Seek trauma-focused therapy (EMDR or CPT)",
            "Join a support group for trauma survivors",
            "Create a safety plan for triggering situations"
        ],
        "BIPOLAR": [
            "Urgent consultation with psychiatrist recommended",
            "Maintain consistent sleep schedule",
            "Monitor mood changes with a daily log"
        ],
        "ADHD": [
            "Consider ADHD-specialized coaching or therapy",
            "Discuss medication options with a specialist",
            "Implement organizational tools and routines"
        ],
        "OCD": [
            "Seek ERP (Exposure and Response Prevention) therapy",
            "Consider SSRI medication with psychiatrist",
            "Avoid reassurance-seeking behaviors"
        ]
    }
    
    recs = base_recs.get(disorder_id, [
        "Schedule follow-up with mental health professional",
        "Maintain healthy lifestyle habits",
        "Build a support network"
    ])
    
    if severity == "severe":
        recs.insert(0, "Urgent: Schedule immediate appointment with mental health professional")
    
    return recs
