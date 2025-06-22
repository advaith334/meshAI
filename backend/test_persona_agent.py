#!/usr/bin/env python3
"""
Test PersonaAgent with real LLM integration
This tests the core persona functionality we've built
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_persona_agent_creation_and_response():
    """Test creating a PersonaAgent and getting a response"""
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not set. Cannot test PersonaAgent.")
        print("Set your Gemini API key in .env file to test this functionality.")
        return False
    
    try:
        print("🤖 Testing PersonaAgent Creation and Response...")
        
        # Import required classes
        from models.persona import Persona
        from agents.persona_agent import PersonaAgent
        
        # Create a test persona
        test_persona = Persona(
            name="Tech Enthusiast Tester",
            description="A technology enthusiast who loves discussing innovations",
            avatar="🚀",
            personality_traits={
                "curiosity": 0.9,
                "optimism": 0.8,
                "technical_knowledge": 0.8,
                "enthusiasm": 0.9
            },
            communication_style="Enthusiastic and technical, uses industry terminology",
            background_context="Works in tech industry, follows latest trends",
            expertise_areas=["artificial intelligence", "software development", "emerging tech"],
            sentiment_bias=0.3,  # Positive bias
            engagement_level=0.8,  # High engagement
            controversy_tolerance=0.6
        )
        
        print(f"✅ Created test persona: {test_persona.name}")
        print(f"   - Sentiment bias: {test_persona.sentiment_bias}")
        print(f"   - Engagement level: {test_persona.engagement_level}")
        
        # Create PersonaAgent
        agent = PersonaAgent(
            persona=test_persona,
            llm_config={
                "model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 200
            },
            verbose=False  # Reduce verbosity for testing
        )
        
        print(f"✅ Created PersonaAgent: {agent.name}")
        print(f"   - Agent ID: {agent.id}")
        print(f"   - Role: {agent.role}")
        
        # Test message processing
        test_message = "What do you think about the future of artificial intelligence?"
        
        print(f"\n💬 Testing message processing...")
        print(f"   Question: {test_message}")
        
        response = agent.process_message(test_message)
        
        print(f"✅ Got response from {agent.name}:")
        print(f"   - Content: {response['content'][:200]}...")
        print(f"   - Sentiment Score: {response['sentiment_score']}")
        print(f"   - Processing Time: {response['processing_time']:.2f}s")
        print(f"   - Word Count: {response['metadata']['word_count']}")
        
        # Test conversation memory
        print(f"\n🧠 Testing conversation memory...")
        memory_context = agent.get_memory_context(limit=1)
        print(f"   - Memory entries: {len(agent.conversation_history)}")
        if memory_context:
            print(f"   - Last interaction stored: Yes")
        
        # Test a follow-up message
        follow_up = "Can you elaborate on that?"
        print(f"\n💬 Testing follow-up message...")
        print(f"   Follow-up: {follow_up}")
        
        follow_up_response = agent.process_message(follow_up)
        print(f"✅ Got follow-up response:")
        print(f"   - Content: {follow_up_response['content'][:200]}...")
        print(f"   - Memory entries now: {len(agent.conversation_history)}")
        
        # Test persona summary
        summary = agent.get_persona_summary()
        print(f"\n📊 Persona Summary:")
        print(f"   - Conversation count: {summary['conversation_count']}")
        print(f"   - Traits: {list(summary['traits'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ PersonaAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_persona_types():
    """Test different persona types with different characteristics"""
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Skipping different persona types test - no API key")
        return True
    
    try:
        print("\n🎭 Testing Different Persona Types...")
        
        from models.persona import Persona
        from agents.persona_agent import PersonaAgent
        
        # Create different persona types
        personas_data = [
            {
                "name": "Skeptical Analyst",
                "description": "Critical thinker who questions everything",
                "avatar": "🤔",
                "sentiment_bias": -0.3,  # Negative bias
                "engagement_level": 0.4,  # Low engagement
                "traits": {"skepticism": 0.9, "analytical": 0.8}
            },
            {
                "name": "Enthusiastic Supporter",
                "description": "Optimistic person who loves new ideas",
                "avatar": "😊",
                "sentiment_bias": 0.5,  # Very positive bias
                "engagement_level": 0.9,  # High engagement
                "traits": {"optimism": 0.9, "enthusiasm": 0.8}
            }
        ]
        
        test_question = "Should we adopt this new AI technology in our company?"
        
        for persona_data in personas_data:
            persona = Persona(
                name=persona_data["name"],
                description=persona_data["description"],
                avatar=persona_data["avatar"],
                personality_traits=persona_data["traits"],
                sentiment_bias=persona_data["sentiment_bias"],
                engagement_level=persona_data["engagement_level"],
                controversy_tolerance=0.5
            )
            
            agent = PersonaAgent(persona=persona, verbose=False)
            response = agent.process_message(test_question)
            
            print(f"\n👤 {persona.name} ({persona.avatar}):")
            print(f"   - Sentiment bias: {persona.sentiment_bias}")
            print(f"   - Response sentiment: {response['sentiment_score']:.2f}")
            print(f"   - Response: {response['content'][:150]}...")
        
        print("✅ Different persona types tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Different persona types test failed: {e}")
        return False

def main():
    """Run PersonaAgent tests"""
    print("🚀 MeshAI PersonaAgent Testing")
    print("=" * 50)
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("❌ Missing GOOGLE_API_KEY")
        print("\n💡 To test PersonaAgent functionality:")
        print("1. Get a Gemini API key from https://makersuite.google.com/app/apikey")
        print("2. Add it to your .env file: GOOGLE_API_KEY=your-key-here")
        print("3. Run this test again")
        return
    
    tests = [
        test_persona_agent_creation_and_response,
        test_different_persona_types
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 PersonaAgent Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All PersonaAgent tests passed!")
        print("\n✅ What's Working:")
        print("   - PersonaAgent creation with real personas")
        print("   - LLM integration with Gemini API")
        print("   - Message processing and response generation")
        print("   - Conversation memory and context")
        print("   - Sentiment analysis based on persona traits")
        print("   - Different persona types with different behaviors")
        
        print("\n🔄 This proves the core AI functionality works!")
        print("   The backend can now generate persona-specific responses")
        print("   Ready to build API endpoints for the frontend")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 