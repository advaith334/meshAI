# MeshAI CrewAI Backend

A powerful backend service that uses CrewAI framework with Google Gemini API to create intelligent AI agent personas for market research, focus groups, and interactive discussions.

## Features

- **10 Distinct AI Personas**: Tech Enthusiast, Price-Sensitive Consumer, Eco-Conscious Expert, Early Adopter, Skeptical Buyer, Marketing Manager, Software Engineer, Product Manager, Sales Executive, and Data Analyst
- **Multi-Modal Interactions**: Simple Q&A, Group Discussions, and Comprehensive Focus Group Simulations
- **Sentiment Analysis**: Real-time sentiment tracking and analysis
- **Professional Market Research**: NPS, CSAT, and detailed analytics
- **YAML-Based Configuration**: Easy persona and task customization
- **RESTful API**: Clean endpoints for frontend integration

## Prerequisites

- Python 3.10+ (required for CrewAI)
- Google Gemini API Key
- Virtual environment (recommended)

## Installation

### 1. Clone and Navigate to Backend
```bash
git clone <repository-url>
cd meshAI/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Get Your Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Running the Backend

```bash
python app.py
```

The backend will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns system status and configuration info.

### Get Available Personas
```
GET /api/personas
```
Returns list of all available AI personas.

### Simple Interaction
```
POST /api/simple-interaction
Content-Type: application/json

{
  "question": "What do you think about this new product?",
  "personas": ["tech-enthusiast", "price-sensitive", "eco-conscious"]
}
```

### Group Discussion
```
POST /api/group-discussion
Content-Type: application/json

{
  "question": "Should we implement this feature?",
  "personas": ["software-engineer", "product-manager", "sales-executive"],
  "initial_reactions": [...]
}
```

### Focus Group Simulation
```
POST /api/focus-group
Content-Type: application/json

{
  "campaign_description": "A new eco-friendly smartphone with solar charging",
  "personas": ["tech-enthusiast", "eco-conscious", "price-sensitive", "early-adopter"],
  "goals": ["Assess market reception", "Identify key concerns", "Evaluate pricing strategy"]
}
```

## Available Personas

| Persona ID | Role | Focus Area |
|------------|------|------------|
| `tech-enthusiast` | Tech Enthusiast and Innovation Expert | Technology trends and innovations |
| `price-sensitive` | Budget-Conscious Consumer Analyst | Cost-benefit analysis and value |
| `eco-conscious` | Environmental Sustainability Expert | Environmental impact and sustainability |
| `early-adopter` | Innovation Early Adopter and Trend Setter | Emerging trends and opportunities |
| `skeptical-buyer` | Critical Analyst and Skeptical Consumer | Risk assessment and critical analysis |
| `marketing-manager` | Strategic Marketing Professional | Brand positioning and market strategy |
| `software-engineer` | Technical Engineering Specialist | Technical feasibility and implementation |
| `product-manager` | Product Strategy and Development Expert | Product-market fit and user needs |
| `sales-executive` | Sales and Revenue Generation Specialist | Sales potential and customer objections |
| `data-analyst` | Data and Analytics Expert | Data quality and analytical insights |

## Configuration

### Adding New Personas
Edit `config/agents.yaml` to add new personas:
```yaml
new_persona:
  role: >
    Your Persona Role
  goal: >
    Your persona's primary goal and motivation
  backstory: >
    Detailed backstory that shapes the persona's behavior and responses
  llm: google/gemini-pro
```

### Adding New Task Types
Edit `config/tasks.yaml` to add new task types:
```yaml
new_task_type:
  description: >
    Task description with placeholders like {topic} and {context}
  expected_output: >
    Description of expected output format
  agent: {agent_name}
```

## Architecture

### CrewManager Class
The `CrewManager` class handles all AI operations:
- Agent creation and caching
- Task execution
- Sentiment analysis
- Multi-round discussions
- Report generation

### Flask Application
Clean REST API with proper error handling and CORS support for frontend integration.

### YAML Configuration
Flexible configuration system allowing easy customization of personas and tasks without code changes.

## Response Formats

### Simple Interaction Response
```json
{
  "question": "Your question",
  "reactions": [
    {
      "persona_id": "tech-enthusiast",
      "name": "Tech Enthusiast and Innovation Expert",
      "avatar": "🤖",
      "reaction": "AI-generated response",
      "sentiment": "positive",
      "sentiment_score": 3
    }
  ],
  "timestamp": "2024-12-19T10:30:00.000Z"
}
```

### Focus Group Response
```json
{
  "campaign_description": "Campaign details",
  "session_goals": ["Goal 1", "Goal 2"],
  "initial_reactions": [...],
  "discussion_messages": [...],
  "sentiment_intervals": [...],
  "final_summary": "AI-generated executive summary",
  "overall_metrics": {
    "nps": 7.5,
    "csat": 4.2,
    "avg_sentiment": 2.1
  },
  "timestamp": "2024-12-19T10:30:00.000Z"
}
```

## Error Handling

All endpoints return consistent error responses:
```json
{
  "error": "Descriptive error message"
}
```

HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing required fields)
- `500`: Internal Server Error

## Development

### Adding New Features
1. Update YAML configurations if needed
2. Add new methods to `CrewManager`
3. Create new Flask endpoints
4. Test with Postman or curl

### Debugging
- Enable verbose mode in CrewAI agents for detailed logs
- Check Flask debug output for request/response details
- Monitor Gemini API usage and rate limits

## Production Deployment

### Environment Variables
Set these in your production environment:
```env
GEMINI_API_KEY=your_production_api_key
FLASK_ENV=production
FLASK_DEBUG=False
```

### Security Considerations
- Keep your Gemini API key secure
- Implement rate limiting for API endpoints
- Add authentication for production use
- Monitor API usage and costs

### Scaling
- Consider using Redis for agent caching
- Implement database storage for conversation history
- Add load balancing for multiple instances
- Monitor memory usage with multiple concurrent requests

## Troubleshooting

### API Key Issues
- Verify your Gemini API key is correct
- Check API key permissions and quotas
- Ensure the API key environment variable is set

### Import Errors
- Confirm Python 3.10+ is being used
- Verify all dependencies are installed
- Check virtual environment is activated

### Configuration Issues
- Verify YAML files are properly formatted
- Check file paths are correct
- Ensure all required configuration fields are present

## Support

For issues related to:
- **CrewAI Framework**: [CrewAI Documentation](https://docs.crewai.com/)
- **Google Gemini API**: [Gemini API Documentation](https://ai.google.dev/)
- **Flask Framework**: [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is part of the MeshAI system. Please refer to the main repository for licensing information. 