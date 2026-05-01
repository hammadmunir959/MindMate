"""
app/agents/graph.py
====================
Unified MindMate AI Orchestrator.
Consolidates interaction (PIA) and clinical logic (DA) into a single StateGraph.
"""

import logging
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from sqlalchemy import select, func

from app.agents.core.config import settings
from app.agents.core.llm_client import get_llm
from app.agents.core.checkpoint import get_postgres_checkpointer
from app.db.session import SessionLocal
from app.models.specialist import Specialist
from app.agents.state import MindMateState
from app.schemas.agent_schemas import (
    SupervisorOutput, ExtractedSymptoms, SupervisorDecision, 
    Symptom, SymptomItem, EscalationFlag, DiagnosisOutput,
    TreatmentPlanOutput
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path & Loading
# ---------------------------------------------------------------------------
PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8") if path.exists() else f"[PROMPT NOT FOUND: {filename}]"

def _load_base_prompt() -> str:
    return _load_prompt("base_system_prompt.md")

def _load_dsm_criteria() -> str:
    return _load_prompt("dsm_criteria.json")

# ---------------------------------------------------------------------------
# Module Prompt Mapping
# ---------------------------------------------------------------------------
MODULE_PROMPT_FILES = {
    "ONBOARDING": "onboarding_prompt.md",
    "SCID_SC": "scid_sc_prompt.md",
    "MDD": "mdd_prompt.md",
    "BIPOLAR": "bipolar_prompt.md",
    "GAD": "gad_prompt.md",
    "PTSD": "ptsd_prompt.md",
    "PANIC": "panic_prompt.md",
    "SOCIAL_ANXIETY": "social_anxiety_prompt.md",
    "OCD": "ocd_prompt.md",
    "ADHD": "adhd_prompt.md",
    "SUBSTANCE_USE": "substance_use_prompt.md",
    "EATING": "eating_prompt.md",
    "RISK": "risk_escalation_prompt.md",
}

# ---------------------------------------------------------------------------
# Node: supervisor
# ---------------------------------------------------------------------------

async def supervisor_node(state: MindMateState) -> dict:
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(SupervisorOutput)

    # Pakistan Standard Time (UTC+5)
    pk_time = datetime.now(timezone(timedelta(hours=5)))
    temporal_context = pk_time.strftime("Current Date: %Y-%m-%d, Day: %A, Time: %I:%M %p PKT")

    dsm_json_str = _load_dsm_criteria()
    sys_prompt_template = _load_prompt("supervisor_prompt.md")
    system_prompt = sys_prompt_template.format(dsm_criteria=dsm_json_str)
    system_prompt = f"--- TEMPORAL CONTEXT: {temporal_context} ---\n\n{system_prompt}"

    # Build context string
    context = f"""
Active Module: {state.get("active_module", "ONBOARDING")}
Modules Visited: {state.get("modules_visited", [])}
Turn Count: {state.get("turn_count", 0)}
Existing Symptoms: {len(state.get("symptoms", []))}

--- Conversation Transcript ---
"""
    for msg in state["messages"]:
        role = "Patient" if msg.type == "human" else "Clinician"
        context += f"\n{role}: {msg.content}"

    try:
        result: SupervisorOutput = await structured_llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=context),
        ])
        return {"supervisor_decision": result.model_dump()}
    except Exception as e:
        logger.error(f"Supervisor parsing failed: {e}")
        return {"supervisor_decision": None}

# ---------------------------------------------------------------------------
# Node: context_manager
# ---------------------------------------------------------------------------

def context_manager_node(state: MindMateState) -> dict:
    decision = state.get("supervisor_decision")
    current_module = state.get("active_module", "ONBOARDING")
    modules_visited = list(state.get("modules_visited", []))
    
    # Determine transitions
    next_module = decision.get("next_module", current_module) if decision else current_module
    is_complete = next_module == "COMPLETE"
    
    if is_complete:
        # Don't change active_module to COMPLETE, keep it for final nodes to have context
        next_module = current_module

    if next_module != current_module and next_module not in modules_visited:
        modules_visited.append(next_module)

    # Temporal & Patient info
    pk_time = datetime.now(timezone(timedelta(hours=5)))
    pk_context_str = pk_time.strftime("Current Date: %Y-%m-%d, Day: %A, Time: %I:%M %p PKT")
    
    p_context = state.get("patient_context", {})
    patient_info_str = f"Gender: {p_context.get('gender', 'Unknown')}, Age: {p_context.get('age', 'Unknown')}, City: {p_context.get('city', 'Unknown')}"

    # Load and Compose Prompt
    base = _load_base_prompt()
    module_file = MODULE_PROMPT_FILES.get(next_module, "onboarding_prompt.md")
    module_prompt = _load_prompt(module_file)
    
    full_system_prompt = (
        f"--- TEMPORAL CONTEXT: {pk_context_str} ---\n"
        f"--- PATIENT DEMOGRAPHICS: {patient_info_str} ---\n\n"
        f"{base}\n\n---\n\n{module_prompt}"
    )

    return {
        "system_prompt": full_system_prompt,
        "active_module": next_module,
        "modules_visited": modules_visited,
        "is_interview_complete": is_complete,
    }

# ---------------------------------------------------------------------------
# Node: call_llm
# ---------------------------------------------------------------------------

async def call_llm_node(state: MindMateState) -> dict:
    full_messages = [SystemMessage(content=state["system_prompt"])] + list(state["messages"])
    llm = get_llm()
    response = await llm.ainvoke(full_messages)
    return {
        "messages": [response],
        "turn_count": state.get("turn_count", 0) + 1,
    }

# ---------------------------------------------------------------------------
# Node: symptoms_extractor
# ---------------------------------------------------------------------------

async def symptoms_extractor_node(state: MindMateState) -> dict:
    recent_msgs = state["messages"][-4:] # Last 2 patient turns approx
    transcript = "\n".join(f"{'Patient' if m.type == 'human' else 'Clinician'}: {m.content}" for m in recent_msgs)
    
    sys_prompt = _load_prompt("extractor_prompt.md")
    llm = get_llm(model=settings.summarizer_llm_model, temperature=0.0)
    structured_llm = llm.with_structured_output(ExtractedSymptoms)
    
    try:
        extraction = await structured_llm.ainvoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=transcript)
        ])
        # Merge logic
        existing = {s['name']: s for s in state.get("symptoms", [])}
        for item in extraction.symptoms:
            existing[item.name] = item.model_dump()
        return {"symptoms": list(existing.values())}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {}

# ---------------------------------------------------------------------------
# Node: summarizer
# ---------------------------------------------------------------------------

async def summarizer_node(state: MindMateState) -> dict:
    messages = list(state["messages"])
    if len(messages) <= 5: return {}
    
    to_compress = messages[:-4]
    to_keep = messages[-4:]
    transcript = "\n".join(f"{'Patient' if m.type == 'human' else 'Clinician'}: {m.content}" for m in to_compress)
    
    llm = get_llm(model=settings.summarizer_llm_model, temperature=0.0)
    sys_prompt = _load_prompt("summarizer_prompt.md")
    response = await llm.ainvoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=transcript)
    ])
    
    summary_text = response.content
    summary_msg = SystemMessage(content=f"[CLINICAL SUMMARY]\n{summary_text}")
    
    existing = state.get("interview_summary") or ""
    return {
        "messages": [summary_msg] + to_keep,
        "interview_summary": f"{existing}\n\n{summary_text}".strip()
    }

# ---------------------------------------------------------------------------
# Node: report_generator
# ---------------------------------------------------------------------------

async def report_generator_node(state: MindMateState) -> dict:
    # Final extraction
    msgs = state["messages"]
    transcript = "\n".join(f"{'Patient' if m.type == 'human' else 'Clinician'}: {m.content}" for m in msgs)
    
    llm = get_llm(temperature=0.0)
    sys_prompt = _load_prompt("report_prompt.md")
    response = await llm.ainvoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=transcript)
    ])
    return {"clinical_report": response.content}

# ---------------------------------------------------------------------------
# DA Nodes (Diagnosis & Treatment)
# ---------------------------------------------------------------------------

async def diagnostician_node(state: MindMateState) -> dict:
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(DiagnosisOutput)
    
    sys_prompt = _load_prompt("diagnostician_prompt.md")
    user_content = f"Clinical Report:\n{state['clinical_report']}\n\nSymptoms:\n{json.dumps(state['symptoms'], indent=2)}"
    
    try:
        diagnosis = await structured_llm.ainvoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_content)
        ])
        return {"diagnosis": diagnosis}
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        return {"errors": [str(e)]}

async def treatment_planner_node(state: MindMateState) -> dict:
    if not state.get("diagnosis"): return {}
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(TreatmentPlanOutput)
    
    sys_prompt = _load_prompt("tpa_prompt.md")
    user_content = f"Diagnosis:\n{json.dumps(state['diagnosis'].model_dump(), indent=2)}\n\nPatient Context:\n{json.dumps(state['patient_context'], indent=2)}"
    
    try:
        plan = await structured_llm.ainvoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_content)
        ])
        return {"treatment_plan": plan.plan_markdown}
    except Exception as e:
        logger.error(f"TPA failed: {e}")
        return {}

async def specialist_matcher_node(state: MindMateState) -> dict:
    if not state.get("diagnosis"): return {}
    
    primary = ""
    if state["diagnosis"].differential_diagnoses:
        primary = state["diagnosis"].differential_diagnoses[0].disorder
        
    city = state["patient_context"].get("city", "")
    
    # DB Call
    db = SessionLocal()
    try:
        query = select(Specialist).where(Specialist.approval_status == "approved")
        if city:
            query = query.where(func.lower(Specialist.city) == city.lower())
        
        result = db.execute(query).scalars().all()
        matches = []
        for s in result:
            matches.append({
                "specialist_id": s.id,
                "name": f"{s.first_name} {s.last_name}",
                "specialization": s.specialist_type.value,
                "location": s.city,
                "match_score": 1.0,
                "reason": f"Matches diagnosis in {s.city}"
            })
        return {"specialists": matches[:3]}
    except Exception as e:
        logger.error(f"Matcher failed: {e}")
        return {}
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Conditional Edges
# ---------------------------------------------------------------------------

def should_continue(state: MindMateState):
    if state.get("is_interview_complete", False):
        return "report_generator"
    return "context_manager"

# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def build_mindmate_graph(checkpointer=None) -> StateGraph:
    builder = StateGraph(MindMateState)
    
    # 1. Add Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("context_manager", context_manager_node)
    builder.add_node("call_llm", call_llm_node)
    builder.add_node("symptoms_extractor", symptoms_extractor_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("report_generator", report_generator_node)
    
    # DA Nodes
    builder.add_node("diagnostician", diagnostician_node)
    builder.add_node("treatment_planner", treatment_planner_node)
    builder.add_node("specialist_matcher", specialist_matcher_node)
    
    # 2. Build Core Loop
    builder.add_edge(START, "supervisor")
    
    # Supervisor -> Continue OR Report
    builder.add_conditional_edges("supervisor", should_continue)
    
    # Interaction Path
    builder.add_edge("context_manager", "call_llm")
    
    # Background cleanup post-LLM call
    builder.add_edge("call_llm", "symptoms_extractor")
    builder.add_edge("symptoms_extractor", "summarizer")
    builder.add_edge("summarizer", END)
    
    # Clinical Path
    builder.add_edge("report_generator", "diagnostician")
    
    # Parallel Clinical Outputs
    builder.add_edge("diagnostician", "treatment_planner")
    builder.add_edge("diagnostician", "specialist_matcher")
    
    builder.add_edge("treatment_planner", END)
    builder.add_edge("specialist_matcher", END)
    
    return builder.compile(checkpointer=checkpointer)

async def get_mindmate_graph():
    checkpointer = await get_postgres_checkpointer()
    return build_mindmate_graph(checkpointer=checkpointer)
