import requests
import json
import os
import logging
from datetime import datetime

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")
        
        if response.text.strip():
            data = response.json()
            print(f"JSON Response: {json.dumps(data, indent=2)}")
        else:
            print("Empty response received")
            data = {}
        
        return {
            "endpoint": "/api/health",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": data
        }
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error - is Flask app running on {BASE_URL}? Error: {e}")
        return {"endpoint": "/api/health", "error": f"Connection error: {e}"}
    except requests.exceptions.Timeout as e:
        print(f"Request timeout: {e}")
        return {"endpoint": "/api/health", "error": f"Timeout: {e}"}
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {"endpoint": "/api/health", "error": f"JSON decode error: {e}"}
    except Exception as e:
        print(f"Error calling health check: {e}")
        return {"endpoint": "/api/health", "error": str(e)}


def test_get_personas():
    """Test the personas endpoint"""
    print("\n=== Testing Get Personas ===")
    try:
        response = requests.get(f"{BASE_URL}/api/personas")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Number of personas: {len(data) if isinstance(data, list) else 'N/A'}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return {
            "endpoint": "/api/personas",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": data
        }
    except Exception as e:
        print(f"Error calling get personas: {e}")
        return {"endpoint": "/api/personas", "error": str(e)}


def test_simple_interaction():
    """Test the simple interaction endpoint"""
    print("\n=== Testing Simple Interaction ===")
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set, skipping this test")
        return {"endpoint": "/api/simple-interaction", "skipped": "GEMINI_API_KEY not set"}
    
    payload = {
        "question": "What do you think about AI?",
        "personas": ["tech-enthusiast"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/simple-interaction",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return {
            "endpoint": "/api/simple-interaction",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": data
        }
    except Exception as e:
        print(f"Error calling simple interaction: {e}")
        return {"endpoint": "/api/simple-interaction", "error": str(e)}

def test_focus_group():
    """Test the focus group simulation endpoint"""
    print("\n=== Testing Focus Group ===")
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set, skipping this test")
        return {"endpoint": "/api/focus-group", "skipped": "GEMINI_API_KEY not set"}
    
    payload = {
        "campaign_description": "New product launch",
        "personas": ["tech-enthusiast"],
        "goals": ["Gather feedback", "Test messaging"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/focus-group",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return {
            "endpoint": "/api/focus-group",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": data
        }
    except Exception as e:
        print(f"Error calling focus group: {e}")
        return {"endpoint": "/api/focus-group", "error": str(e)}


def test_custom_persona():
    """Test the custom persona creation endpoint"""
    print("\n=== Testing Custom Persona ===")
    payload = {
        "name": "Custom Tester",
        "role": "QA Engineer", 
        "industry": "Software",
        "description": "Focused on quality assurance and testing",
        "avatar": "🧪",
        "customAttributes": {"experience": "5 years"},
        "motivations": ["Quality", "Efficiency"],
        "behavioralTraits": ["Detail-oriented", "Methodical"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/custom-persona",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        return {
            "endpoint": "/api/custom-persona",
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": data
        }
    except Exception as e:
        print(f"Error calling custom persona: {e}")
        return {"endpoint": "/api/custom-persona", "error": str(e)}


def check_server_connection():
    """Check if the Flask server is running"""
    print("\n=== Checking Server Connection ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running on {BASE_URL}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure your Flask app is running:")
        print("  cd meshAI/backend")
        print("  source venv/bin/activate")
        print("  python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("=== MeshAI Backend API Tests ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # First check if server is running
    if not check_server_connection():
        return []
    
    results = []
    
    # Run all tests
    results.append(test_health_check())
    results.append(test_get_personas())
    results.append(test_simple_interaction())
    results.append(test_focus_group())
    results.append(test_custom_persona())
    
    # Print summary
    print("\n=== Test Summary ===")
    for result in results:
        endpoint = result.get('endpoint', 'Unknown')
        if 'error' in result:
            print(f"❌ {endpoint}: ERROR - {result['error']}")
        elif 'skipped' in result:
            print(f"⏭️  {endpoint}: SKIPPED - {result['skipped']}")
        elif result.get('success'):
            print(f"✅ {endpoint}: SUCCESS")
        else:
            print(f"❌ {endpoint}: FAILED - Status {result.get('status_code')}")
    
    return results


if __name__ == '__main__':
    run_all_tests() 