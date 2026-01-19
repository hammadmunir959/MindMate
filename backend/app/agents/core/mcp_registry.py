"""
MCP Tool Registry
=================
Central registry for all MCP tools across agents.
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    handler: Callable
    input_schema: Dict[str, Any]
    agent: str  # Which agent owns this tool


class MCPToolRegistry:
    """
    Central registry for MCP tools.
    Agents register their tools here for discovery and execution.
    """
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._agents: Dict[str, List[str]] = {}  # agent -> tool names
    
    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
        input_schema: Dict[str, Any],
        agent: str
    ):
        """Register a tool"""
        tool = MCPTool(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
            agent=agent
        )
        self._tools[name] = tool
        
        if agent not in self._agents:
            self._agents[agent] = []
        self._agents[agent].append(name)
        
        logger.debug(f"Registered MCP tool: {name} (agent: {agent})")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, agent: Optional[str] = None) -> List[Dict]:
        """List all tools or tools for a specific agent"""
        if agent:
            tool_names = self._agents.get(agent, [])
            tools = [self._tools[n] for n in tool_names if n in self._tools]
        else:
            tools = list(self._tools.values())
        
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "agent": t.agent
            }
            for t in tools
        ]
    
    async def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        """Call a tool by name"""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        try:
            result = tool.handler(**params)
            # Handle both sync and async
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            raise


# Global registry singleton
_registry = MCPToolRegistry()


def get_registry() -> MCPToolRegistry:
    """Get the global tool registry"""
    return _registry


def register_tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    agent: str
):
    """Decorator to register a function as an MCP tool"""
    def decorator(func: Callable):
        _registry.register(
            name=name,
            description=description,
            handler=func,
            input_schema=input_schema,
            agent=agent
        )
        return func
    return decorator


__all__ = ["MCPToolRegistry", "MCPTool", "get_registry", "register_tool"]
