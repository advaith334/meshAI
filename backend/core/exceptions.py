class MeshAIException(Exception):
    """Base exception for MeshAI application"""
    
    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self):
        """Convert exception to dictionary for API responses"""
        return {
            'error': True,
            'message': self.message,
            'code': self.code,
            'details': self.details
        }

class ValidationError(MeshAIException):
    """Raised when input validation fails"""
    
    def __init__(self, message, field=None, value=None):
        super().__init__(message, code='VALIDATION_ERROR')
        self.field = field
        self.value = value
        if field:
            self.details['field'] = field
        if value is not None:
            self.details['value'] = value

class AgentError(MeshAIException):
    """Raised when agent operations fail"""
    
    def __init__(self, message, agent_type=None, agent_id=None):
        super().__init__(message, code='AGENT_ERROR')
        self.agent_type = agent_type
        self.agent_id = agent_id
        if agent_type:
            self.details['agent_type'] = agent_type
        if agent_id:
            self.details['agent_id'] = agent_id

class PersonaError(MeshAIException):
    """Raised when persona operations fail"""
    
    def __init__(self, message, persona_id=None):
        super().__init__(message, code='PERSONA_ERROR')
        self.persona_id = persona_id
        if persona_id:
            self.details['persona_id'] = persona_id

class ConversationError(MeshAIException):
    """Raised when conversation operations fail"""
    
    def __init__(self, message, conversation_id=None):
        super().__init__(message, code='CONVERSATION_ERROR')
        self.conversation_id = conversation_id
        if conversation_id:
            self.details['conversation_id'] = conversation_id

class FocusGroupError(MeshAIException):
    """Raised when focus group operations fail"""
    
    def __init__(self, message, focus_group_id=None):
        super().__init__(message, code='FOCUS_GROUP_ERROR')
        self.focus_group_id = focus_group_id
        if focus_group_id:
            self.details['focus_group_id'] = focus_group_id

class LLMError(MeshAIException):
    """Raised when LLM operations fail"""
    
    def __init__(self, message, provider=None, model=None):
        super().__init__(message, code='LLM_ERROR')
        self.provider = provider
        self.model = model
        if provider:
            self.details['provider'] = provider
        if model:
            self.details['model'] = model

class RateLimitError(MeshAIException):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, message, limit=None, reset_time=None):
        super().__init__(message, code='RATE_LIMIT_ERROR')
        self.limit = limit
        self.reset_time = reset_time
        if limit:
            self.details['limit'] = limit
        if reset_time:
            self.details['reset_time'] = reset_time 