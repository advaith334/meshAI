from typing import Dict, Type, Any, Optional
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Container:
    """Dependency injection container for managing services"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance"""
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: callable) -> None:
        """Register a factory function for creating instances"""
        self._factories[name] = factory
    
    def register_service(self, name: str, service_class: Type, **kwargs) -> None:
        """Register a service class with initialization parameters"""
        self._services[name] = {'class': service_class, 'kwargs': kwargs}
    
    def get(self, name: str) -> Any:
        """Get a service instance"""
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            instance = self._factories[name]()
            return instance
        
        # Check registered services
        if name in self._services:
            service_config = self._services[name]
            instance = service_config['class'](**service_config['kwargs'])
            return instance
        
        raise ValueError(f"Service '{name}' not found in container")
    
    def get_singleton(self, name: str) -> Any:
        """Get or create a singleton instance"""
        if name in self._singletons:
            return self._singletons[name]
        
        # Create and store as singleton
        instance = self.get(name)
        self._singletons[name] = instance
        return instance
    
    def has(self, name: str) -> bool:
        """Check if a service is registered"""
        return (name in self._singletons or 
                name in self._factories or 
                name in self._services)
    
    def clear(self) -> None:
        """Clear all registered services"""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()

# Global container instance
container = Container()

def setup_container(config):
    """Setup the dependency injection container with core services"""
    
    # Database setup
    engine = create_engine(
        config.SQLALCHEMY_DATABASE_URI,
        echo=config.SQLALCHEMY_ECHO if hasattr(config, 'SQLALCHEMY_ECHO') else False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    container.register_singleton('db_engine', engine)
    container.register_factory('db_session', SessionLocal)
    
    # Redis setup
    if config.REDIS_URL:
        redis_client = redis.from_url(config.REDIS_URL)
        container.register_singleton('redis', redis_client)
    
    # Configuration
    container.register_singleton('config', config)
    
    return container

def get_container() -> Container:
    """Get the global container instance"""
    return container 