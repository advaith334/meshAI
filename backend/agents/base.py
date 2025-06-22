from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
import uuid
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from core.logging import agent_logger
from core.exceptions import AgentError, LLMError

class BaseAgent(ABC):
    """Base class for all MeshAI agents"""
    
    def __init__(self, 
                 name: str,
                 role: str, 
                 goal: str,
                 backstory: str,
                 llm_config: Dict[str, Any] = None,
                 verbose: bool = True,
                 memory: bool = True):
        
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.memory = memory
        
        # Initialize LLM
        self.llm = self._setup_llm(llm_config or {})
        
        # Initialize CrewAI agent
        self.agent = self._create_crew_agent()
        
        # Conversation memory
        self.conversation_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        
        agent_logger.info(f"Initialized {self.__class__.__name__}", 
                         agent_id=self.id, name=self.name, role=self.role)
    
    def _setup_llm(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """Setup the LLM for this agent"""
        try:
            return ChatGoogleGenerativeAI(
                model=config.get('model', 'gemini-2.0-flash-exp'),
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 1000),
                verbose=self.verbose,
                timeout=30  # Add timeout to prevent hanging
            )
        except Exception as e:
            raise LLMError(f"Failed to initialize LLM: {str(e)}")
    
    def _create_crew_agent(self) -> Agent:
        """Create the CrewAI agent instance"""
        try:
            return Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                verbose=self.verbose,
                memory=self.memory,
                llm=self.llm,
                allow_delegation=False
            )
        except Exception as e:
            raise AgentError(f"Failed to create CrewAI agent: {str(e)}", 
                           agent_type=self.__class__.__name__, agent_id=self.id)
    
    @abstractmethod
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message and return a response"""
        pass
    
    def add_to_memory(self, message: str, response: str, metadata: Dict[str, Any] = None):
        """Add interaction to conversation memory"""
        entry = {
            'timestamp': time.time(),
            'message': message,
            'response': response,
            'metadata': metadata or {}
        }
        self.conversation_history.append(entry)
        
        # Keep only last 50 interactions to prevent memory bloat
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_memory_context(self, limit: int = 10) -> str:
        """Get recent conversation history as context"""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-limit:]
        context_parts = []
        
        for entry in recent:
            context_parts.append(f"Human: {entry['message']}")
            context_parts.append(f"Assistant: {entry['response']}")
        
        return "\n".join(context_parts)
    
    def update_context(self, key: str, value: Any):
        """Update agent context"""
        self.context[key] = value
        agent_logger.debug(f"Updated context for {self.name}", 
                          agent_id=self.id, key=key)
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from agent context"""
        return self.context.get(key, default)
    
    def reset_memory(self):
        """Clear conversation memory"""
        self.conversation_history.clear()
        self.context.clear()
        agent_logger.info(f"Reset memory for {self.name}", agent_id=self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'goal': self.goal,
            'backstory': self.backstory,
            'type': self.__class__.__name__,
            'memory_size': len(self.conversation_history),
            'context_keys': list(self.context.keys())
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} ({self.id[:8]})>" 