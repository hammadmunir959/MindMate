"""
MCP Tool Server
===============
Exposes Diagnosis Agent tools via MCP protocol.
"""

from typing import Dict, List, Any, Optional
import json
import logging

from app.agents.diagnosis.tools import TOOLS, get_tool, list_tools

logger = logging.getLogger(__name__)


class MCPToolServer:
    """
    MCP-style tool server for Diagnosis Agent.
    
    Provides a standardized interface for tool discovery and execution.
    Can be extended to support actual MCP protocol over stdio/http.
    """
    
    def __init__(self, llm_client=None, criteria_db: Dict = None):
        self.llm_client = llm_client
        self.criteria_db = criteria_db
        self._load_criteria()
    
    def _load_criteria(self):
        """Load DSM-5 criteria if not provided."""
        if self.criteria_db is None:
            import os
            base_path = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_path, "resources", "dsm_criteria.json")
            
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                    self.criteria_db = data.get("disorders", {})
            except Exception as e:
                logger.error(f"Failed to load criteria: {e}")
                self.criteria_db = {}
    
    def list_tools(self) -> List[Dict]:
        """
        MCP: List available tools.
        
        Returns tool schemas in MCP format.
        """
        return list_tools()
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        MCP: Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool = get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        
        execute_fn = tool["execute"]
        
        # Inject dependencies
        if tool_name == "screen_categories":
            return await execute_fn(
                symptoms=arguments.get("symptoms", []),
                llm_client=self.llm_client
            )
        
        elif tool_name == "get_candidate_disorders":
            return await execute_fn(
                categories=arguments.get("categories", []),
                symptoms=arguments.get("symptoms", [])
            )
        
        elif tool_name == "evaluate_criteria":
            return await execute_fn(
                disorder_id=arguments.get("disorder_id", ""),
                symptoms=arguments.get("symptoms", []),
                criteria_db=self.criteria_db,
                llm_client=self.llm_client
            )
        
        elif tool_name == "generate_report":
            return await execute_fn(
                diagnoses=arguments.get("diagnoses", []),
                symptoms=arguments.get("symptoms", []),
                llm_client=self.llm_client
            )
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a specific tool."""
        tool = get_tool(tool_name)
        return tool["schema"] if tool else None


# Export
__all__ = ["MCPToolServer"]
