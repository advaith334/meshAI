import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app_config):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app_config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, app_config.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (rotating)
    if app_config.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            app_config.LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, app_config.LOG_LEVEL.upper()))
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Specific loggers
    setup_specific_loggers()
    
    logging.info("Logging configured successfully")

def setup_specific_loggers():
    """Setup specific loggers for different components"""
    
    # Agent logger
    agent_logger = logging.getLogger('meshai.agents')
    agent_logger.setLevel(logging.DEBUG)
    
    # LLM logger
    llm_logger = logging.getLogger('meshai.llm')
    llm_logger.setLevel(logging.DEBUG)
    
    # Database logger
    db_logger = logging.getLogger('meshai.database')
    db_logger.setLevel(logging.INFO)
    
    # API logger
    api_logger = logging.getLogger('meshai.api')
    api_logger.setLevel(logging.INFO)
    
    # CrewAI logger (reduce verbosity)
    crew_logger = logging.getLogger('crewai')
    crew_logger.setLevel(logging.WARNING)
    
    # Langchain logger (reduce verbosity)
    langchain_logger = logging.getLogger('langchain')
    langchain_logger.setLevel(logging.WARNING)

def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(f'meshai.{name}')

class StructuredLogger:
    """Structured logger for consistent logging across the application"""
    
    def __init__(self, name):
        self.logger = get_logger(name)
    
    def info(self, message, **kwargs):
        """Log info message with structured data"""
        self._log(logging.INFO, message, kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message with structured data"""
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message, **kwargs):
        """Log error message with structured data"""
        self._log(logging.ERROR, message, kwargs)
    
    def debug(self, message, **kwargs):
        """Log debug message with structured data"""
        self._log(logging.DEBUG, message, kwargs)
    
    def _log(self, level, message, data):
        """Internal logging method"""
        if data:
            extra_info = " | ".join([f"{k}={v}" for k, v in data.items()])
            full_message = f"{message} | {extra_info}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)

# Pre-configured loggers for common use cases
agent_logger = StructuredLogger('agents')
llm_logger = StructuredLogger('llm')
api_logger = StructuredLogger('api')
db_logger = StructuredLogger('database') 