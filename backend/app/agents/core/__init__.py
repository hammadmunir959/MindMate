"""
Core Agent Package
==================
Central types, state, and MCP registry for all agents.
"""

from app.agents.core.types import (
    ResponseType, Severity, ConversationPhase, RiskLevel, ModuleStatus,
    Symptom, SCIDQuestion, ProcessedResponse, ConversationState,
    AgentOutput, TherapistOutput, SRAOutput, DiagnosisOutput
)
from app.agents.core.state import StateManager, get_state_manager
from app.agents.core.mcp_registry import MCPToolRegistry, get_registry, register_tool

__all__ = [
    # Types
    "ResponseType", "Severity", "ConversationPhase", "RiskLevel", "ModuleStatus",
    "Symptom", "SCIDQuestion", "ProcessedResponse", "ConversationState",
    "AgentOutput", "TherapistOutput", "SRAOutput", "DiagnosisOutput",
    # State
    "StateManager", "get_state_manager",
    # MCP
    "MCPToolRegistry", "get_registry", "register_tool"
]
