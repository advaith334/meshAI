#!/usr/bin/env python3
"""
Debug script to test Gemini API calls and identify hanging issues
"""
import os
import time
import sys
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, trying manual load...")
    # Manual .env loading
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Manually loaded .env file")

def test_environment():
    """Check environment setup"""
    print("🔍 Environment Check")
    print("-" * 30)
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
        return False
    else:
        print(f"✅ GOOGLE_API_KEY set (length: {len(api_key)})")
        print(f"   Key starts with: {api_key[:10]}...")
    
    return True

def test_basic_import():
    """Test basic imports"""
    print("\n📦 Testing Imports")
    print("-" * 30)
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported")
    except ImportError as e:
        print(f"❌ google.generativeai import failed: {e}")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai imported")
    except ImportError as e:
        print(f"❌ langchain_google_genai import failed: {e}")
        return False
    
    return True

def test_direct_google_api():
    """Test direct Google Generative AI API"""
    print("\n🤖 Testing Direct Google API")
    print("-" * 30)
    
    try:
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
        
        # Create model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Model created successfully")
        
        # Simple test with timeout
        print("🔄 Making API call...")
        start_time = time.time()
        
        response = model.generate_content(
            "Say 'Hello from Gemini!' in exactly 3 words.",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10,
                temperature=0.1,
            )
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Direct API call successful!")
        print(f"   Response: {response.text}")
        print(f"   Duration: {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_langchain_api():
    """Test LangChain wrapper"""
    print("\n🔗 Testing LangChain Wrapper")
    print("-" * 30)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Create LLM with minimal config
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=10,
            timeout=10  # 10 second timeout
        )
        print("✅ LangChain LLM created successfully")
        
        # Simple test
        print("🔄 Making LangChain API call...")
        start_time = time.time()
        
        response = llm.invoke("Say 'Hello LangChain!'")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ LangChain API call successful!")
        print(f"   Response: {response.content}")
        print(f"   Duration: {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_with_different_configs():
    """Test different configurations to find optimal settings"""
    print("\n⚙️ Testing Different Configurations")
    print("-" * 30)
    
    configs = [
        {"model": "gemini-2.0-flash-exp", "temperature": 0.1, "max_tokens": 5},
        {"model": "gemini-2.0-flash-exp", "temperature": 0.5, "max_tokens": 20},
        {"model": "gemini-2.0-flash-exp", "temperature": 0.7, "max_tokens": 50},
    ]
    
    successful_configs = []
    
    for i, config in enumerate(configs, 1):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            print(f"\n🧪 Config {i}: {config}")
            
            llm = ChatGoogleGenerativeAI(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                timeout=15
            )
            
            start_time = time.time()
            response = llm.invoke("Hello")
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ✅ Success! Duration: {duration:.2f}s")
            print(f"   Response: {response.content[:50]}...")
            
            successful_configs.append((config, duration))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    if successful_configs:
        print(f"\n🎉 {len(successful_configs)} configurations worked!")
        fastest = min(successful_configs, key=lambda x: x[1])
        print(f"⚡ Fastest config: {fastest[0]} ({fastest[1]:.2f}s)")
    
    return successful_configs

def main():
    """Run all debug tests"""
    print("🚀 Gemini API Debug Session")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    tests = [
        ("Environment", test_environment),
        ("Imports", test_basic_import),
        ("Direct API", test_direct_google_api),
        ("LangChain", test_langchain_api),
        ("Configurations", test_with_different_configs)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n⚠️ Test '{test_name}' interrupted by user")
            results[test_name] = False
            break
        except Exception as e:
            print(f"\n💥 Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Debug Summary")
    print(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if not results.get("Environment", False):
        print("\n💡 Next steps: Set GOOGLE_API_KEY environment variable")
    elif not results.get("Direct API", False):
        print("\n💡 Next steps: Check API key validity and network connection")
    elif not results.get("LangChain", False):
        print("\n💡 Next steps: LangChain wrapper issue - use direct API")
    else:
        print("\n🎉 All tests passed! Gemini API is working correctly.")

if __name__ == "__main__":
    main() 