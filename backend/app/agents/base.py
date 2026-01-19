"""
MindMate Base Agent
===================
Abstract base class for all MindMate AI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from app.core.llm_client import LLMClient


class AgentOutput:
    """Standard output from any agent"""
    
    def __init__(
        self,
        content: Any,
        metadata: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        self.content = content
        self.metadata = metadata or {}
        self.error = error
        self.success = error is None
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "error": self.error,
            "success": self.success
        }


class BaseAgent(ABC):
    """
    Abstract base class for all MindMate agents.
    
    All agents share:
    - Access to LLM client
    - Logging
    - Standard input/output patterns
    - Error handling
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        agent_name: Optional[str] = None
    ):
        self.name = agent_name or self.__class__.__name__
        self.llm = llm_client or LLMClient()
        self.logger = logging.getLogger(f"agents.{self.name}")
    
    @abstractmethod
    async def process(self, state: Dict) -> AgentOutput:
        """
        Process the current state and return output.
        
        Args:
            state: Current conversation/workflow state
            
        Returns:
            AgentOutput with results and metadata
        """
        pass
    
    def log_info(self, message: str):
        """Log info level message"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error level message"""
        self.logger.error(f"[{self.name}] {message}", exc_info=exc_info)
    
    def log_debug(self, message: str):
        """Log debug level message"""
        self.logger.debug(f"[{self.name}] {message}")


__all__ = ["BaseAgent", "AgentOutput"]
