# MeshAI - an simulation of AI Agent Community

MeshAI is a simulation of AI community. In this prototype use case, it is used for AI-powered focus groups that enables businesses to manage custom AI personas, conduct interactive focus groups for multi-modal research, and view dedtailed analytics. 

### **Architecture & Tech Stack**

- Frontend (React + TypeScript)
- Backend (Python + Flask)
- AI & ML: CrewAI, Google Gemini, LangChain

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
