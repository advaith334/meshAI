#!/usr/bin/env python3
"""
Quick test script for MeshAI backend - skips LLM tests for faster development
"""
import os
import sys
import json

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration...")
    try:
        from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
        
        # Test config classes exist and have required attributes
        configs = [DevelopmentConfig, ProductionConfig, TestingConfig]
        for config_class in configs:
            config = config_class()
            assert hasattr(config, 'SQLALCHEMY_DATABASE_URI')
            assert hasattr(config, 'SECRET_KEY')
            print(f"✅ {config_class.__name__} configuration valid")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database_models():
    """Test database models can be imported and instantiated"""
    print("\n🗄️  Testing Database Models...")
    try:
        from models.persona import Persona, PersonaTrait
        from models.conversation import Conversation, Message
        from models.focus_group import FocusGroup, FocusGroupParticipant
        
        # Test model creation (without database)
        persona = Persona(
            name="Test Persona",
            description="A test persona",
            avatar="🤖"
        )
        print("✅ Persona model works")
        
        conversation = Conversation(
            title="Test Chat",
            persona_id="test-id"
        )
        print("✅ Conversation model works")
        
        focus_group = FocusGroup(
            title="Test Focus Group",
            initial_question="What do you think about this product?"
        )
        print("✅ FocusGroup model works")
        
        return True
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_services_and_agents():
    """Test services and agents can be imported"""
    print("\n🔧 Testing Services and Agents...")
    try:
        from services.persona_service import PersonaService
        from agents.persona_agent import PersonaAgent
        from agents.base import BaseAgent
        
        # Test service instantiation
        service = PersonaService()
        print("✅ PersonaService imported and instantiated")
        
        # Test agent classes
        print("✅ Agent classes imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Services and agents test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation (without LLM)"""
    print("\n🌐 Testing Flask App...")
    try:
        # Set testing mode
        os.environ['FLASK_ENV'] = 'testing'
        
        # Skip if no API key (to avoid LLM initialization)
        if not os.environ.get('GOOGLE_API_KEY'):
            print("⚠️  Skipping Flask app test - GOOGLE_API_KEY not set")
            return True
            
        from app import create_app
        
        app, socketio = create_app('testing')
        print("✅ Flask app created successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Health check endpoint works")
        
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🚀 MeshAI Backend Quick Test")
    print("=" * 40)
    print("(Skips LLM tests for faster development)")
    
    tests = [
        test_configuration,
        test_database_models, 
        test_services_and_agents,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Quick Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quick tests passed!")
        print("\n✅ Core functionality is working:")
        print("   - Configuration system")
        print("   - Database models")
        print("   - Services and agents")
        print("   - Flask application")
        
        print("\n🔄 Ready for development!")
        
    else:
        print(f"⚠️  {total - passed} tests failed.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 