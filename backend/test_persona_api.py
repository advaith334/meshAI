#!/usr/bin/env python3
"""
Test script for Persona API endpoints
"""
import requests
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

BASE_URL = "http://localhost:5000/api/personas"

def test_api_endpoints():
    """Test all Persona API endpoints"""
    print("🧪 Testing Persona API Endpoints")
    print("=" * 50)
    
    # Test 1: List personas
    print("\n1️⃣ Testing GET /api/personas")
    try:
        response = requests.get(BASE_URL)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['count']} personas")
            personas = data['data']
            if personas:
                print(f"   First persona: {personas[0]['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Get specific persona
    print("\n2️⃣ Testing GET /api/personas/{id}")
    try:
        # First get list to find an ID
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            personas = response.json()['data']
            if personas:
                persona_id = personas[0]['id']
                response = requests.get(f"{BASE_URL}/{persona_id}")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    persona = response.json()['data']
                    print(f"   ✅ Retrieved persona: {persona['name']}")
                else:
                    print(f"   ❌ Error: {response.text}")
            else:
                print("   ⚠️  No personas found to test with")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create new persona
    print("\n3️⃣ Testing POST /api/personas")
    test_persona = {
        "name": "Test API Persona",
        "description": "A persona created via API for testing",
        "avatar": "🧪",
        "personality_traits": {
            "curiosity": 0.8,
            "optimism": 0.6,
            "analytical": 0.7
        },
        "communication_style": "Technical and precise",
        "sentiment_bias": 0.1,
        "engagement_level": 0.8
    }
    
    try:
        response = requests.post(
            BASE_URL,
            json=test_persona,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            created_persona = response.json()['data']
            print(f"   ✅ Created persona: {created_persona['name']}")
            print(f"   ID: {created_persona['id']}")
            
            # Store ID for update/delete tests
            test_persona_id = created_persona['id']
            
            # Test 4: Update persona
            print("\n4️⃣ Testing PUT /api/personas/{id}")
            update_data = {
                "description": "Updated description via API test",
                "sentiment_bias": 0.2
            }
            
            response = requests.put(
                f"{BASE_URL}/{test_persona_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                updated_persona = response.json()['data']
                print(f"   ✅ Updated persona: {updated_persona['name']}")
                print(f"   New description: {updated_persona['description'][:50]}...")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # Test 5: Delete persona
            print("\n5️⃣ Testing DELETE /api/personas/{id}")
            response = requests.delete(f"{BASE_URL}/{test_persona_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Deleted persona successfully")
            else:
                print(f"   ❌ Error: {response.text}")
                
        else:
            print(f"   ❌ Error creating persona: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Test validation
    print("\n6️⃣ Testing validation (invalid data)")
    invalid_persona = {
        "name": "",  # Invalid: empty name
        "description": "Test"
    }
    
    try:
        response = requests.post(
            BASE_URL,
            json=invalid_persona,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            error_data = response.json()
            print(f"   ✅ Validation working: {error_data['message']}")
        else:
            print(f"   ❌ Expected validation error, got: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    print("\n💡 To run this test:")
    print("   1. Start the Flask server: python app.py")
    print("   2. Run this test: python test_persona_api.py")

if __name__ == "__main__":
    test_api_endpoints() 