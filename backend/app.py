import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from crew_manager import CrewManager

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize CrewManager
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

crew_manager = CrewManager(gemini_api_key)

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
        campaign_description = data.get("campaign_description", "")
        selected_personas = data.get("personas", [])
        session_goals = data.get("goals", [])
        
        if not campaign_description or not selected_personas:
            return jsonify({"error": "Campaign description and personas are required"}), 400
        
        result = crew_manager.run_focus_group_simulation(
            campaign_description, selected_personas, session_goals
        )
        
        return jsonify(result)
        
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
