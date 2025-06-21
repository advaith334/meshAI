#!/usr/bin/env python3
"""
Test script for MeshAI CrewAI Backend
Run this to verify your backend is working correctly
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Gemini configured: {data['gemini_configured']}")
            print(f"   Agents loaded: {data['agents_loaded']}")
            print(f"   Tasks loaded: {data['tasks_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_personas():
    """Test getting available personas"""
    print("\n👥 Testing get personas...")
    try:
        response = requests.get(f"{BASE_URL}/api/personas")
        if response.status_code == 200:
            personas = response.json()
            print(f"✅ Retrieved {len(personas)} personas")
            for persona in personas[:3]:  # Show first 3
                print(f"   {persona['avatar']} {persona['name']}")
            return True
        else:
            print(f"❌ Get personas failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get personas error: {e}")
        return False

def test_simple_interaction():
    """Test simple interaction endpoint"""
    print("\n💬 Testing simple interaction...")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Skipping AI interaction tests - GEMINI_API_KEY not set")
        return True
    
    try:
        payload = {
            "question": "What do you think about sustainable technology?",
            "personas": ["tech-enthusiast", "eco-conscious", "skeptical-buyer"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/simple-interaction",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simple interaction successful")
            print(f"   Question: {data['question']}")
            print(f"   Reactions: {len(data['reactions'])}")
            
            for reaction in data['reactions']:
                print(f"   {reaction['avatar']} {reaction['name']}: {reaction['sentiment']}")
                print(f"      \"{reaction['reaction'][:80]}...\"")
            return True
        else:
            print(f"❌ Simple interaction failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Simple interaction error: {e}")
        return False

def test_focus_group():
    """Test focus group simulation (lightweight version)"""
    print("\n🎯 Testing focus group simulation...")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Skipping AI interaction tests - GEMINI_API_KEY not set")
        return True
    
    try:
        payload = {
            "campaign_description": "A new app that helps people track their carbon footprint",
            "personas": ["eco-conscious", "tech-enthusiast"],  # Reduced for testing
            "goals": ["Assess initial reaction", "Identify concerns"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/focus-group",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Focus group simulation successful")
            print(f"   Campaign: {data['campaign_description'][:50]}...")
            print(f"   Initial reactions: {len(data['initial_reactions'])}")
            print(f"   Discussion messages: {len(data['discussion_messages'])}")
            print(f"   Overall NPS: {data['overall_metrics']['nps']}")
            return True
        else:
            print(f"❌ Focus group failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Focus group error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MeshAI CrewAI Backend Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
    except:
        print("❌ Backend server is not running!")
        print("   Please start the server with: python app.py")
        return
    
    tests = [
        test_health_check,
        test_get_personas,
        test_simple_interaction,
        # test_focus_group,  # Uncomment for full testing (takes longer)
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("\n💡 Tip: Set GEMINI_API_KEY in your .env file to test AI functionality")

if __name__ == "__main__":
    main() 