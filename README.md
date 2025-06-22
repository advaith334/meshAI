# meshAI

MeshAI is a full-stack platform for simulating intelligent AI agent personas for market research, focus groups, and interactive discussions. It leverages a powerful Python backend (CrewAI + Google Gemini API) and a modern React/TypeScript frontend for seamless, multi-modal user experiences.

---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Setup & Installation](#setup--installation)
  - [Backend](#backend-setup)
  - [Frontend](#frontend-setup)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Available Personas](#available-personas)
- [Development & Contribution](#development--contribution)
- [Troubleshooting](#troubleshooting)
- [Support & Resources](#support--resources)
- [License](#license)

---

## Features
- **20+ Distinct AI Personas**: Simulate a wide range of market participants, experts, and consumers.
- **Multi-Modal Interactions**: Simple Q&A, group discussions, and comprehensive focus group simulations.
- **Sentiment Analysis**: Real-time sentiment tracking and analytics.
- **Professional Market Research**: NPS, CSAT, and detailed analytics.
- **YAML-Based Configuration**: Easily add or modify personas and tasks.
- **RESTful API**: Clean endpoints for frontend integration.
- **Modern UI**: Responsive, component-driven React/TypeScript frontend with Tailwind CSS.

---

## Architecture

### Backend
- **Framework**: Python 3.10+, Flask, CrewAI, Google Gemini API
- **Key Files**:
  - `app.py`: Main Flask app, API endpoints
  - `crew_manager.py`: Core logic for agent management, task execution, sentiment analysis
  - `config/agents.yaml`: Persona definitions
  - `config/tasks.yaml`: Task templates
  - `personas/`: Individual persona JSON files
  - `test_backend.py`: Backend tests

### Frontend
- **Framework**: React, TypeScript, Vite, Tailwind CSS
- **Key Files**:
  - `src/pages/`: Main app pages (Dashboard, FocusGroup, UserInterface, etc.)
  - `src/components/`: UI and persona components
  - `src/lib/api.ts`: API integration helpers
  - `src/hooks/`: Custom React hooks
  - `public/`: Static assets

---

## Setup & Installation

### Backend Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meshAI/backend
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**
   - Create a `.env` file in `backend/`:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     FLASK_ENV=development
     FLASK_DEBUG=True
     ```
   - Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
5. **Run the backend**
   ```bash
   python app.py
   ```
   The backend will start on `http://localhost:5000`

### Frontend Setup
1. **Navigate to frontend**
   ```bash
   cd ../frontend
   ```
2. **Install dependencies**
   ```bash
   npm install
   # or
   bun install
   ```
3. **Run the frontend**
   ```bash
   npm run dev
   # or
   bun run dev
   ```
   The frontend will start on `http://localhost:5173`

---

## Configuration

### Personas
- Defined in `backend/config/agents.yaml` and `backend/personas/`
- Add or modify personas by editing these files

### Tasks
- Defined in `backend/config/tasks.yaml`
- Add or modify task templates for new research scenarios

---

## API Endpoints

### Health Check
```http
GET /api/health
```
Returns system status and configuration info.

### Get Available Personas
```http
GET /api/personas
```
Returns list of all available AI personas.

### Simple Interaction
```http
POST /api/simple-interaction
Content-Type: application/json
{
  "question": "What do you think about this new product?",
  "personas": ["tech-enthusiast", "price-sensitive", "eco-conscious"]
}
```

### Group Discussion
```http
POST /api/group-discussion
Content-Type: application/json
{
  "question": "Should we implement this feature?",
  "personas": ["software-engineer", "product-manager", "sales-executive"],
  "initial_reactions": [...]
}
```

### Focus Group Simulation
```http
POST /api/focus-group
Content-Type: application/json
{
  "campaign_description": "A new eco-friendly smartphone with solar charging",
  "personas": ["tech-enthusiast", "eco-conscious", "price-sensitive", "early-adopter"],
  "goals": ["Assess market reception", "Identify key concerns", "Evaluate pricing strategy"]
}
```

#### Response Formats
- See `backend/README.md` for detailed response examples for each endpoint.

---

## Available Personas

A sample of available personas (see `backend/personas/` for all):

| Persona File | Description |
|--------------|-------------|
| Tech_Enthusiast.json | Technology trends and innovations |
| BudgetConciousCustomer.json | Cost-benefit analysis and value |
| Environmental_Sustainability_Expert.json | Environmental impact and sustainability |
| Early_Adopter_and_Trend_Setter.json | Emerging trends and opportunities |
| Technical_Engineering_Specialist.json | Technical feasibility and implementation |
| Marketing Manager | Brand positioning and market strategy |
| Data Analyst | Data quality and analytical insights |
| ... | ... |

To add new personas, edit `config/agents.yaml` and add a new JSON file in `personas/`.

---

## Development & Contribution

- **Backend**: Add new features in `crew_manager.py`, update Flask endpoints in `app.py`, and expand YAML configs.
- **Frontend**: Add new pages/components in `src/pages/` and `src/components/`.
- **Testing**: Use `test_backend.py` for backend tests. Add frontend tests as needed.
- **Pull Requests**: Please open issues or pull requests for major changes.

---

## Troubleshooting

- **API Key Issues**: Ensure your Gemini API key is correct and set in `.env`.
- **Import Errors**: Use Python 3.10+ and activate your virtual environment.
- **Configuration Issues**: Check YAML formatting and required fields.
- **Frontend Issues**: Ensure Node.js, npm, or bun are installed and up to date.

---

## Support & Resources
- [CrewAI Documentation](https://docs.crewai.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## License

This project is part of the MeshAI system. Please refer to the repository for licensing information.
