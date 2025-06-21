import pytest
import json
import os
import logging
from app import app

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client





class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        # Log the health response
        logger.info(f"Health check response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert isinstance(data['gemini_configured'], bool)
        assert isinstance(data['agents_loaded'], int)
        assert isinstance(data['tasks_loaded'], int)
        assert data['agents_loaded'] > 0, f"Expected agents to be loaded but got {data['agents_loaded']}"
        assert data['tasks_loaded'] > 0, f"Expected tasks to be loaded but got {data['tasks_loaded']}"
        
        # Check if Gemini is actually configured
        assert data['gemini_configured'] is True, "GEMINI_API_KEY should be configured"

class TestCrewAIInitialization:
    """Test CrewAI initialization and configuration"""
    
    def test_crew_manager_initialization(self, client):
        """Test that CrewManager initializes correctly"""
        # Import here to see if initialization fails
        from app import crew_manager
        
        logger.info(f"CrewManager LLM: {crew_manager.llm}")
        logger.info(f"Agents config keys: {list(crew_manager.agents_config.keys())}")
        logger.info(f"Tasks config keys: {list(crew_manager.tasks_config.keys())}")
        
        # Check that configs are loaded
        assert len(crew_manager.agents_config) > 0, "No agents configuration loaded"
        assert len(crew_manager.tasks_config) > 0, "No tasks configuration loaded"
        
        # Check that required agents exist
        expected_agents = ['tech_enthusiast', 'price_sensitive', 'eco_conscious']
        for agent_name in expected_agents:
            assert agent_name in crew_manager.agents_config, f"Agent {agent_name} not found in config"
            
        # Test creating an agent
        agent = crew_manager.create_agent('tech_enthusiast')
        assert agent is not None, "Failed to create tech_enthusiast agent"
        logger.info(f"Created agent: {agent.role}")
        
        # Test creating a task
        task = crew_manager.create_task('initial_reaction_task', agent, 
                                       topic="Test question", 
                                       context="Test context",
                                       agent_name="tech_enthusiast")
        assert task is not None, "Failed to create initial_reaction_task"
        logger.info(f"Created task: {task.description[:100]}...")


class TestPersonasEndpoint:
    """Test the personas endpoint"""
    
    def test_get_personas_success(self, client):
        """Test successful retrieval of personas"""
        response = client.get('/api/personas')
        data = json.loads(response.data)
        
        # Log the personas response
        logger.info(f"Personas response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) > 0, f"Expected personas but got empty list"
        
        # Check structure of first persona
        persona = data[0]
        assert 'id' in persona
        assert 'name' in persona
        assert 'description' in persona
        assert 'avatar' in persona
        
        # Check for some expected personas
        persona_ids = [p['id'] for p in data]
        logger.info(f"Available persona IDs: {persona_ids}")
        expected_personas = ['tech-enthusiast', 'price-sensitive', 'eco-conscious']
        for expected in expected_personas:
            assert expected in persona_ids, f"Expected persona '{expected}' not found in {persona_ids}"


class TestSimpleInteractionEndpoint:
    """Test the simple interaction endpoint"""
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
    def test_simple_interaction_success(self, client):
        """Test successful simple interaction"""
        payload = {
            "question": "What do you think about AI?",
            "personas": ["tech-enthusiast"]
        }
        
        response = client.post('/api/simple-interaction', 
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        # Log the full response to see what we're getting
        logger.info(f"Simple interaction response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['question'] == "What do you think about AI?"
        assert 'reactions' in data
        assert 'timestamp' in data
        assert isinstance(data['reactions'], list)
        
        # Make test more strict - we MUST have reactions
        assert len(data['reactions']) > 0, f"Expected reactions but got empty list. Full response: {data}"
        
        reaction = data['reactions'][0]
        assert 'persona_id' in reaction
        assert 'name' in reaction
        assert 'avatar' in reaction
        assert 'reaction' in reaction
        assert 'sentiment' in reaction
        assert 'sentiment_score' in reaction
        assert reaction['persona_id'] == 'tech-enthusiast'
        
        # Check that we got a real response, not just an error message
        assert len(reaction['reaction']) > 10, f"Reaction too short, might be an error: {reaction['reaction']}"
        assert not reaction['reaction'].startswith("Error"), f"Got error in reaction: {reaction['reaction']}"
    
    def test_simple_interaction_missing_question(self, client):
        """Test simple interaction with missing question"""
        payload = {"personas": ["tech-enthusiast"]}
        
        response = client.post('/api/simple-interaction',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Question and personas are required'
    
    def test_simple_interaction_missing_personas(self, client):
        """Test simple interaction with missing personas"""
        payload = {"question": "What do you think about AI?"}
        
        response = client.post('/api/simple-interaction',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Question and personas are required'
    
    def test_simple_interaction_empty_personas(self, client):
        """Test simple interaction with empty personas list"""
        payload = {
            "question": "What do you think about AI?",
            "personas": []
        }
        
        response = client.post('/api/simple-interaction',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Question and personas are required'
    
    def test_simple_interaction_invalid_persona(self, client):
        """Test simple interaction with invalid persona"""
        payload = {
            "question": "What do you think about AI?",
            "personas": ["nonexistent-persona"]
        }
        
        response = client.post('/api/simple-interaction',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        # The endpoint should still return 200 but with empty or error reactions
        # depending on implementation
        assert response.status_code in [200, 500]


class TestGroupDiscussionEndpoint:
    """Test the group discussion endpoint"""
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
    def test_group_discussion_success(self, client):
        """Test successful group discussion"""
        payload = {
            "question": "What do you think about AI?",
            "personas": ["tech-enthusiast"],
            "initial_reactions": [
                {
                    "persona_id": "tech-enthusiast",
                    "name": "Tech Enthusiast",
                    "reaction": "Initial reaction",
                    "sentiment": "neutral"
                }
            ]
        }
        
        response = client.post('/api/group-discussion',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        # Log the full response to see what we're getting
        logger.info(f"Group discussion response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['question'] == "What do you think about AI?"
        assert 'discussion_messages' in data
        assert 'timestamp' in data
        assert isinstance(data['discussion_messages'], list)
        
        # Make test more strict - we should have discussion messages
        assert len(data['discussion_messages']) > 0, f"Expected discussion messages but got empty list. Full response: {data}"
        
        # Validate the structure of discussion messages
        message = data['discussion_messages'][0]
        required_fields = ['id', 'persona_id', 'persona_name', 'avatar', 'content', 'sentiment', 'timestamp', 'round']
        for field in required_fields:
            assert field in message, f"Missing field '{field}' in discussion message: {message}"
        
        # Check that we got real content, not just an error
        assert len(message['content']) > 10, f"Message content too short, might be an error: {message['content']}"
    
    def test_group_discussion_missing_data(self, client):
        """Test group discussion with missing required data"""
        payload = {"personas": ["tech-enthusiast"]}
        
        response = client.post('/api/group-discussion',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Question and personas are required'


class TestFocusGroupEndpoint:
    """Test the focus group simulation endpoint"""
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
    def test_focus_group_success(self, client):
        """Test successful focus group simulation"""
        payload = {
            "campaign_description": "New product launch",
            "personas": ["tech-enthusiast"],
            "goals": ["Gather feedback", "Test messaging"]
        }
        
        response = client.post('/api/focus-group',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['campaign_description'] == "New product launch"
        assert 'initial_reactions' in data
        assert 'discussion_messages' in data
        assert 'final_summary' in data
        assert 'overall_metrics' in data
        assert 'timestamp' in data
        
        # Check structure of overall_metrics
        metrics = data['overall_metrics']
        assert 'nps' in metrics
        assert 'csat' in metrics
        assert 'avg_sentiment' in metrics
    
    def test_focus_group_missing_campaign(self, client):
        """Test focus group with missing campaign description"""
        payload = {"personas": ["tech-enthusiast"]}
        
        response = client.post('/api/focus-group',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Campaign description and personas are required'
    
    def test_focus_group_missing_personas(self, client):
        """Test focus group with missing personas"""
        payload = {"campaign_description": "New product launch"}
        
        response = client.post('/api/focus-group',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Campaign description and personas are required'


class TestCustomPersonaEndpoint:
    """Test the custom persona creation endpoint"""
    
    def test_create_custom_persona_success(self, client):
        """Test successful custom persona creation"""
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
        
        response = client.post('/api/custom-persona',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'persona' in data
        assert data['persona']['name'] == 'Custom Tester'
        assert data['persona']['role'] == 'QA Engineer'
        assert data['persona']['avatar'] == '🧪'
        assert data['message'] == 'Custom persona created successfully'
        assert data['persona']['id'].startswith('custom-')
    
    def test_create_custom_persona_with_defaults(self, client):
        """Test custom persona creation with default values"""
        payload = {}  # Empty payload to test defaults
        
        response = client.post('/api/custom-persona',
                             data=json.dumps(payload),
                             content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['persona']['name'] == ''
        assert data['persona']['avatar'] == '👤'
        assert data['persona']['attributes'] == {}
        assert data['persona']['motivations'] == []
        assert data['persona']['traits'] == []


class TestIndexEndpoint:
    """Test the index endpoint"""
    
    def test_index_success(self, client):
        """Test the index endpoint"""
        response = client.get('/')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['message'] == 'MeshAI CrewAI Backend'
        assert data['status'] == 'running'


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_invalid_json_payload(self, client):
        """Test endpoints with invalid JSON payload"""
        response = client.post('/api/simple-interaction',
                             data='invalid json',
                             content_type='application/json')
        
        # Flask returns 500 for JSON parsing errors, not 400
        assert response.status_code == 500
    
    def test_missing_content_type(self, client):
        """Test endpoints without proper content type"""
        payload = {"question": "test", "personas": ["tech-enthusiast"]}
        
        response = client.post('/api/simple-interaction',
                             data=json.dumps(payload))
        
        # Should still work but might have different behavior
        assert response.status_code in [200, 400, 500]


if __name__ == '__main__':
    pytest.main([__file__]) 