# MeshAI - AI-Powered Interview & Focus Group Platform

MeshAI is a comprehensive platform that enables users to conduct AI-powered interviews and focus groups using persona-based interactions. Built with React, TypeScript, and Python, it leverages Google's Gemini AI to create realistic conversations and generate actionable insights.

## 🚀 Features

### **Session Management**
- **One-on-One Interviews**: Conduct focused interviews with individual personas
- **Focus Group Discussions**: Facilitate group discussions with multiple personas
- **Session History**: View, search, and export all previous sessions
- **Real-time Analytics**: Get instant insights and metrics from your sessions

### **AI-Powered Personas**
- **Pre-built Personas**: 20+ diverse personas including Steve Jobs, Oprah Winfrey, Peter Thiel, and more
- **Custom Personas**: Create and save your own personas with specific traits and backgrounds
- **Gemini AI Integration**: All persona responses generated using Google's Gemini 2.5 Flash
- **Dynamic Conversations**: Real-time, context-aware responses based on conversation flow

### **Advanced Analytics**
- **AI-Generated Insights**: Gemini AI analyzes conversations to provide actionable insights
- **Sentiment Analysis**: Track emotional responses and engagement levels
- **Session Metrics**: Duration, message count, participant engagement
- **Export Functionality**: Download session transcripts and analytics as JSON

### **User Experience**
- **Modern UI**: Clean, responsive interface built with Tailwind CSS and shadcn/ui
- **Real-time Chat**: Live conversation interface with typing indicators
- **Session Recording**: Track session duration and participant interactions
- **Search & Filter**: Easily find and filter through session history

## 🏗️ Architecture

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Main application pages
│   ├── lib/           # API client and utilities
│   └── hooks/         # Custom React hooks
```

### **Backend (Python + Flask)**
```
backend/
├── app.py             # Main Flask application
├── crew_manager.py    # CrewAI integration for persona management
├── personas/          # JSON persona definitions
├── prev_prompts/      # Saved session data
└── config/           # YAML configuration files
```

## 🛠️ Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Google Gemini API key

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Start the Backend
```bash
cd backend
python app.py
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

## 📖 Usage Guide

### **Starting a New Session**

1. **Navigate to Dashboard**: Access the main dashboard to see all your sessions
2. **Click "New Session"**: Choose between Interview or Focus Group
3. **Configure Session**:
   - Set session name and purpose
   - Select personas (1 for interview, 2+ for focus group)
   - Add research goals (focus groups only)
4. **Start Session**: Begin the AI-powered conversation

### **Conducting Interviews**

- **One-on-One Interaction**: Chat directly with a single persona
- **Real-time Responses**: Get instant, context-aware responses from Gemini AI
- **Session Control**: End session when ready to view analytics
- **AI Insights**: Automatically generated insights based on conversation content

### **Running Focus Groups**

- **Multi-Persona Discussions**: Up to 20 personas can participate
- **Structured Rounds**: 3 discussion rounds with initial reactions
- **Group Dynamics**: Personas respond to each other's comments
- **Comprehensive Analytics**: Detailed breakdown by participant

### **Viewing Analytics**

- **Session Overview**: Duration, participants, message count
- **AI-Generated Insights**: 8 actionable insights from Gemini AI
- **Sentiment Analysis**: Positive, neutral, and negative sentiment tracking
- **Export Options**: Download session data as JSON

### **Session History**

- **Browse All Sessions**: View interviews and focus groups
- **Search & Filter**: Find sessions by type, date, or content
- **Export Sessions**: Download complete session data
- **Participant Details**: See which personas participated in each session

## 🎭 Available Personas

### **Business & Technology**
- **Steve Jobs**: Design and User Experience Visionary
- **Peter Thiel**: Technology and Investment Expert
- **Tim Cook**: Operations and Supply Chain Specialist
- **Seth Godin**: Marketing and Branding Expert

### **Media & Influence**
- **Oprah Winfrey**: Media and Communication Expert
- **Nate Silver**: Data and Analytics Specialist
- **Seth Godin**: Marketing and Branding Expert

### **Customer Types**
- **Tech Enthusiast**: Early adopter and technology lover
- **Budget Conscious Customer**: Price-sensitive consumer
- **Early Adopter**: Trend-setting consumer
- **Environmental Sustainability Expert**: Eco-conscious specialist

### **Professional Roles**
- **Technical Engineering Specialist**: Engineering and technical expert
- **Jasmine Williams**: Customer Success Manager
- **Marcus Thompson**: Sales Director
- **Maya Chen**: Product Manager
- **Ruby Martinez**: UX Designer
- **Zoe Kim**: Data Scientist

## 🔧 API Endpoints

### **Session Management**
- `GET /api/dashboard-sessions` - Get sessions for dashboard
- `POST /api/save-session` - Save session data
- `GET /api/get-sessions` - Retrieve all saved sessions

### **Persona Management**
- `GET /api/personas` - Get available personas
- `GET /display-personas` - Get personas for display
- `POST /api/custom-persona` - Create custom persona

### **AI Interactions**
- `POST /api/simple-interaction` - One-on-one persona interaction
- `POST /api/focus-group-start` - Start focus group session
- `POST /api/focus-group-round` - Run focus group discussion round
- `POST /api/generate-insights` - Generate AI insights from conversation

### **Health & Status**
- `GET /api/health` - Health check endpoint
- `GET /` - API status and information

## 🎯 Use Cases

### **Product Research**
- Test product concepts with diverse personas
- Gather feedback on features and pricing
- Understand user needs and pain points

### **Market Research**
- Explore market opportunities
- Analyze competitive positioning
- Validate business assumptions

### **User Experience Design**
- Test interface designs and user flows
- Gather feedback on usability
- Identify improvement opportunities

### **Content Development**
- Test messaging and positioning
- Validate content strategies
- Gather insights for marketing campaigns

## 🔒 Security & Privacy

- **Local Storage**: All session data stored locally in `prev_prompts/`
- **No External Storage**: No data sent to external databases
- **API Key Security**: Gemini API key stored in environment variables
- **Session Privacy**: Each session is isolated and private

## 🚀 Deployment

### **Development**
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && python app.py
```

### **Production**
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && gunicorn app:app
```

## 🔮 Future Enhancements

- **Voice Integration**: Add voice-to-text and text-to-speech capabilities
- **Advanced Analytics**: More detailed sentiment and engagement metrics
- **Persona Training**: Allow custom training of persona responses
- **Multi-language Support**: Support for conversations in multiple languages
- **Integration APIs**: Connect with external tools and platforms

---

**MeshAI** - Transforming how you conduct research and gather insights with AI-powered personas.
