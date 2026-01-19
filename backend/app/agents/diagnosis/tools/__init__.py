"""
Diagnosis Tools Init
====================
Exports all MCP tools for the Diagnosis Agent.
"""

from app.agents.diagnosis.tools import screen_categories
from app.agents.diagnosis.tools import get_candidates
from app.agents.diagnosis.tools import evaluate_criteria
from app.agents.diagnosis.tools import generate_report

# Tool registry for MCP
TOOLS = {
    "screen_categories": {
        "schema": screen_categories.TOOL_SCHEMA,
        "execute": screen_categories.execute
    },
    "get_candidate_disorders": {
        "schema": get_candidates.TOOL_SCHEMA,
        "execute": get_candidates.execute
    },
    "evaluate_criteria": {
        "schema": evaluate_criteria.TOOL_SCHEMA,
        "execute": evaluate_criteria.execute
    },
    "generate_report": {
        "schema": generate_report.TOOL_SCHEMA,
        "execute": generate_report.execute
    }
}


def get_tool(name: str):
    """Get a tool by name."""
    return TOOLS.get(name)


def list_tools():
    """List all available tools."""
    return [
        {"name": name, "schema": tool["schema"]}
        for name, tool in TOOLS.items()
    ]


__all__ = ["TOOLS", "get_tool", "list_tools"]
