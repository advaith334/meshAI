# MeshAI - an simulation of AI Agent Communigyt

An innovative platform that transforms traditional market research. Demo use case focuses on AI-powered focus groups, enabling businesses to gather authentic insights from AI agents with customized personas that simulate real customer behaviors and perspectives.

## Inspiration

The inspiration for MeshAI came from wanting to simulate the human community using Ai agents, or building a community of AI agents, which we believed had such a huge scope of potential application. We decided to zoom in to a very specific use case of focus groups due to the challenges businesses face in conducting traditional focus groups - high costs, scheduling difficulties, limited participant diversity, and geographic constraints. We envisioned a world where companies could instantly access diverse perspectives from AI personas that authentically represent different demographics, psychographics, and behavioral patterns. 

Our vision was to democratize market research by making high-quality consumer insights accessible to businesses of all sizes, from startups to enterprises, while maintaining the authenticity and depth of human feedback through advanced AI simulation.

## What it does

MeshAI is a simulation of AI community. In the prototype use case, it is used for AI-powered focus groups that enables businesses to:

### 🎭 **AI Persona Management**
- Create and customize AI personas with detailed backgrounds, demographics, and behavioral traits
- Choose from 20+ pre-built personas including industry experts, consumer archetypes, and notable figures
- Each persona maintains consistent personality, opinions, and decision-making patterns across sessions

### 🗣️ **Interactive Focus Groups**
- Conduct real-time focus group sessions with multiple AI personas
- Simulate authentic group dynamics with natural conversation flow
- Generate streaming responses that mimic real human interaction patterns

### 📊 **Advanced analytics**
- Real-time sentiment analysis of participant responses
- NPS (Net Promoter Score) and CSAT (Customer Satisfaction) metrics
- Comprehensive reporting with insights extraction and trend analysis

### 🎯 **Multi-Modal Research**
- Simple Q&A interactions for quick feedback
- Group discussions with dynamic persona interactions
- Structured focus group sessions with defined goals and outcomes

## How we built it

### **Architecture & Tech Stack**

**Frontend (React + TypeScript)**
- **Framework**: React 18 with TypeScript for type safety
- **Build Tool**: Vite for fast development and optimized builds
- **UI Components**: Radix UI primitives with shadcn/ui design system
- **Styling**: Tailwind CSS for responsive, modern design
- **State Management**: React hooks with custom API client
- **Routing**: React Router DOM for navigation

**Backend (Python + Flask)**
- **Framework**: Flask with CORS support for API endpoints
- **AI Orchestration**: CrewAI for managing multiple AI agents
- **LLM Integration**: Google Gemini 2.5 Flash via LangChain
- **Configuration**: YAML-based agent and task management
- **Data Storage**: JSON-based persona storage with file system management

**AI & ML Components**
- **CrewAI**: Multi-agent AI framework for persona simulation
- **Google Gemini**: Advanced language model for natural conversations
- **LangChain**: LLM integration and prompt management
- **Custom Sentiment Analysis**: Real-time emotion and satisfaction scoring

### **Key Implementation Details**

1. **Multi-Agent AI System**: Each persona is implemented as a separate CrewAI agent with unique:
   - Role definitions and goals
   - Background stories and motivations  
   - Consistent personality traits
   - Memory across conversations

2. **Real-time Communication**: 
   - RESTful API endpoints for seamless frontend-backend communication
   - Streaming responses for natural conversation flow
   - Error handling and fallback mechanisms

3. **Persona Engine**:
   - Dynamic persona loading from JSON configurations
   - Customizable persona creation with avatar selection
   - Persistent persona storage and retrieval

4. **Analytics Pipeline**:
   - Real-time sentiment analysis using AI-powered text analysis
   - Automatic NPS and CSAT score generation
   - Comprehensive session analytics and reporting

## Challenges we ran into

### **1. Multi-Agent Coordination**
Managing multiple AI personas in a single conversation while maintaining individual personality consistency was complex. We solved this by:
- Implementing careful prompt engineering for each persona
- Using CrewAI's task orchestration to manage conversation flow
- Creating memory systems to maintain context across interactions

### **2. Real-time AI Response Generation**
Generating authentic, real-time responses from multiple AI agents simultaneously presented performance challenges:
- Optimized LLM API calls with proper rate limiting
- Implemented response caching and streaming
- Built fallback mechanisms for API failures

### **3. Sentiment Analysis Accuracy**
Creating accurate sentiment analysis that captures nuanced emotional responses:
- Developed custom sentiment scoring algorithms
- Integrated multiple AI models for cross-validation
- Fine-tuned analysis parameters for marketing context

### **4. Dependency Management**
Managing complex Python dependencies with LangChain, CrewAI, and Google AI:
- Resolved version conflicts between packages
- Created isolated virtual environments
- Implemented comprehensive error handling

### **5. User Experience Design**
Designing an interface that makes AI-powered focus groups feel natural and intuitive:
- Iterative UI/UX testing and refinement
- Real-time visual feedback for AI responses
- Responsive design for various screen sizes

## Accomplishments that we're proud of

### **🚀 Technical Achievements**
- **Seamless Multi-Agent AI Integration**: Successfully orchestrated 20+ AI personas with distinct personalities
- **Real-time Conversation Engine**: Built streaming AI responses that feel natural and engaging
- **Advanced Analytics Dashboard**: Created comprehensive insights extraction from AI conversations
- **Scalable Architecture**: Designed a system that can handle multiple concurrent focus group sessions

### **💡 Innovation**
- **AI Persona Authenticity**: Achieved remarkable consistency in persona behavior across different scenarios
- **Dynamic Group Interactions**: Enabled AI personas to interact with each other, not just respond to prompts
- **Sentiment Intelligence**: Developed sophisticated emotion and satisfaction analysis for market research

### **🎨 User Experience**
- **Intuitive Interface**: Created a user-friendly platform that requires no AI expertise
- **Professional Analytics**: Built enterprise-grade reporting and insights visualization
- **Customization Freedom**: Enabled users to create and modify personas for specific research needs

### **⚡ Performance**
- **Fast Response Times**: Optimized AI response generation for real-time conversations
- **Reliable System**: Implemented robust error handling and fallback mechanisms
- **Scalable Infrastructure**: Built a foundation that can grow with user demand

## What we learned

### **AI Development Insights**
- **Prompt Engineering is Critical**: The quality of AI persona responses heavily depends on carefully crafted prompts and context
- **Multi-Agent Complexity**: Managing multiple AI agents requires sophisticated orchestration and memory management
- **LLM Integration Challenges**: Working with different AI models requires understanding their unique capabilities and limitations

### **User Experience Design**
- **AI Interface Design**: Learned how to make AI interactions feel natural and trustworthy
- **Data Visualization**: Discovered effective ways to present complex analytics in digestible formats
- **Responsive Design**: Ensured the platform works seamlessly across devices


## What's next for Mesh AI

### **🌟 Long-term Vision**

**Global Platform**
- **International Expansion**: Support for global markets with localized personas
- **Compliance Framework**: GDPR, CCPA, and other privacy regulation compliance
- **Mobile Applications**: Native iOS and Android apps for on-the-go research

**AI Innovation**
- **Hybrid AI-Human Groups**: Combine AI personas with real human participants
- **Virtual Reality Integration**: Immersive focus group experiences
- **Emotional AI**: Advanced emotion recognition and response generation

**Market Expansion**
- **Academic Research**: Tools for universities and research institutions
- **Government Applications**: Public policy research and citizen engagement
- **Non-profit Sector**: Accessible research tools for social impact organizations

---

## 🛠️ Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Google AI API key

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/advaith334/meshAI.git
   cd meshAI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip3 install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Create .env file in backend directory
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd backend && source venv/bin/activate && python app.py
   
   # Terminal 2 - Frontend  
   cd frontend && npm run dev
   ```

6. **Access the Platform**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000

---

**Built with ❤️ for the future of market research**

*MeshAI - Where AI meets authentic consumer insights*
