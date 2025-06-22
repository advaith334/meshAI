import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from crew_manager import CrewManager
from crewai import Crew, Process

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This ensures logs go to console/terminal
    ]
)

# Set Flask's logger to INFO level as well
app.logger.setLevel(logging.INFO)

# Initialize CrewManager
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

crew_manager = CrewManager(gemini_api_key)

# Test log to confirm logging is working
app.logger.info("MeshAI Backend started successfully - logging is configured!")

@app.route("/")
def index():
    return jsonify({"message": "MeshAI CrewAI Backend", "status": "running"})

@app.route("/api/personas", methods=["GET"])
def get_personas():
    """Get available personas"""
    try:
        personas = crew_manager.get_available_personas()
        return jsonify(personas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/simple-interaction", methods=["POST"])
def simple_interaction():
    """Handle simple Q&A interaction with selected personas"""
    try:
        data = request.json
        question = data.get("question", "")
        selected_personas = data.get("personas", [])
        
        if not question or not selected_personas:
            return jsonify({"error": "Question and personas are required"}), 400
        
        reactions = crew_manager.run_simple_interaction(question, selected_personas)
        
        app.logger.info(f"Reactions: {reactions}")
        
        return jsonify({
            "question": question,
            "reactions": reactions,
            "timestamp": crew_manager._get_timestamp()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/group-discussion", methods=["POST"])
def group_discussion():
    """Handle group discussion between personas"""
    try:
        data = request.json
        question = data.get("question", "")
        selected_personas = data.get("personas", [])
        initial_reactions = data.get("initial_reactions", [])
        
        if not question or not selected_personas:
            return jsonify({"error": "Question and personas are required"}), 400
        
        discussion_messages = crew_manager.run_group_discussion(
            question, selected_personas, initial_reactions
        )
        
        app.logger.info(f"Discussion Messages: {discussion_messages}")
        
        return jsonify({
            "question": question,
            "discussion_messages": discussion_messages,
            "timestamp": crew_manager._get_timestamp()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/focus-group", methods=["POST"])
def focus_group_simulation():
    """Handle focus group simulation"""
    try:
        data = request.json
        app.logger.info(f"Focus Group Data: {data}")
        campaign_description = data.get("campaign_description", "")
        selected_personas = data.get("personas", [])
        session_goals = data.get("goals", [])
        
        if not campaign_description or not selected_personas:
            return jsonify({"error": "Campaign description and personas are required"}), 400
        
        result = crew_manager.run_focus_group_simulation(
            campaign_description, selected_personas, session_goals
        )
        
        app.logger.info(f"Focus Group Result: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/focus-group-start", methods=["POST"])
def focus_group_start():
    """Start focus group with initial reactions"""
    try:
        data = request.json
        app.logger.info(f"Focus Group Start Data: {data}")
        campaign_description = data.get("campaign_description", "")
        selected_personas = data.get("personas", [])
        session_goals = data.get("goals", [])
        
        if not campaign_description or not selected_personas:
            return jsonify({"error": "Campaign description and personas are required"}), 400
        
        # Only run Phase 1: Initial Reactions
        initial_reactions = []
        
        for persona_id in selected_personas:
            agent_name = persona_id.replace('-', '_')
            agent = crew_manager.create_agent(agent_name)
            
            if not agent:
                app.logger.error(f"Failed to create agent for {agent_name}")
                continue
            
            task = crew_manager.create_task(
                'focus_group_initial_task',
                agent,
                campaign_description=campaign_description,
                session_goals=", ".join(session_goals),
                agent_name=agent_name
            )
            
            if not task:
                app.logger.error(f"Failed to create task for {agent_name}")
                continue
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                response_text = str(result)
                app.logger.info(f"Initial Reaction for {persona_id}: {len(response_text)} characters")
                sentiment, score = crew_manager._analyze_sentiment(response_text)
                
                persona_config = crew_manager.agents_config[agent_name]
                
                initial_reactions.append({
                    "id": crew_manager._generate_uuid(),
                    "persona_id": persona_id,
                    "persona_name": persona_config['role'].strip(),  # Remove newlines
                    "avatar": crew_manager._get_avatar_for_persona(persona_id),
                    "content": response_text.strip(),  # Remove extra whitespace
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "timestamp": crew_manager._get_timestamp(),
                    "round": 0  # Initial reactions are round 0
                })
                
            except Exception as e:
                app.logger.error(f"Error in initial reaction for {persona_id}: {e}")
                import traceback
                app.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            "phase": "initial_reactions",
            "messages": initial_reactions,
            "timestamp": crew_manager._get_timestamp()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/focus-group-round", methods=["POST"])
def focus_group_round():
    """Run a single discussion round"""
    try:
        data = request.json
        campaign_description = data.get("campaign_description", "")
        selected_personas = data.get("personas", [])
        round_number = data.get("round_number", 1)
        previous_messages = data.get("previous_messages", [])
        
        if not campaign_description or not selected_personas:
            return jsonify({"error": "Campaign description and personas are required"}), 400
        
        round_messages = []
        
        for persona_id in selected_personas:
            agent_name = persona_id.replace('-', '_')
            agent = crew_manager.create_agent(agent_name)
            
            if not agent:
                continue
            
            # Create context from previous messages (excluding this persona's own messages)
            recent_messages = [m for m in previous_messages[-6:] if m.get("persona_id") != persona_id]
            recent_context = "\n".join([f"{m.get('persona_name', 'Unknown')}: {m.get('content', '')}" for m in recent_messages])
            
            task = crew_manager.create_task(
                'focus_group_discussion_task',
                agent,
                campaign_description=campaign_description,
                recent_context=recent_context or "This is the start of the discussion.",
                round_number=round_number,
                agent_name=agent_name
            )
            
            if not task:
                continue
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                response_text = str(result)
                app.logger.info(f"Round {round_number} Response for {persona_id}: {response_text}")
                sentiment, score = crew_manager._analyze_sentiment(response_text)
                
                persona_config = crew_manager.agents_config[agent_name]
                
                round_messages.append({
                    "id": crew_manager._generate_uuid(),
                    "persona_id": persona_id,
                    "persona_name": persona_config['role'].strip(),  # Remove newlines
                    "avatar": crew_manager._get_avatar_for_persona(persona_id),
                    "content": response_text.strip(),  # Remove extra whitespace
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "timestamp": crew_manager._get_timestamp(),
                    "round": round_number
                })
                
            except Exception as e:
                app.logger.error(f"Error in round {round_number} for {persona_id}: {e}")
        
        return jsonify({
            "phase": f"round_{round_number}",
            "round_number": round_number,
            "messages": round_messages,
            "timestamp": crew_manager._get_timestamp()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/custom-persona", methods=["POST"])
def create_custom_persona():
    """Create a custom persona"""
    try:
        data = request.json
        
        # Extract persona details
        persona_data = {
            "id": f"custom-{crew_manager._generate_uuid()}",
            "name": data.get("name", ""),
            "role": data.get("role", ""),
            "industry": data.get("industry", ""),
            "backstory": data.get("description", ""),
            "avatar": data.get("avatar", "👤"),
            "attributes": data.get("customAttributes", {}),
            "motivations": data.get("motivations", []),
            "traits": data.get("behavioralTraits", [])
        }
        
        app.logger.info(f"Custom Persona Created: {persona_data}")
        
        return jsonify({
            "success": True,
            "persona": persona_data,
            "message": "Custom persona created successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": crew_manager._get_timestamp(),
        "gemini_configured": bool(gemini_api_key),
        "agents_loaded": len(crew_manager.agents_config),
        "tasks_loaded": len(crew_manager.tasks_config)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
