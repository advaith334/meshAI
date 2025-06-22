import os
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from crew_manager import CrewManager

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

# Saving personas to /backend/personas
@app.route("/save-persona", methods=["POST"])
def save_persona():
    new_persona = request.get_json()

    if not new_persona:
        return jsonify({"error": "No data provided"}), 400

    # Create personas directory if it doesn't exist
    personas_dir = "personas"
    if not os.path.exists(personas_dir):
        os.makedirs(personas_dir)

    # Generate a unique filename based on persona name
    persona_name = new_persona.get("name", "unknown")
    # Sanitize the name for use as a filename
    safe_name = "".join(c for c in persona_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    # Add timestamp to ensure uniqueness
    import time
    timestamp = int(time.time())
    filename = f"{safe_name}_{timestamp}.json"
    filepath = os.path.join(personas_dir, filename)

    try:
        with open(filepath, 'w') as f:
            json.dump(new_persona, f, indent=4)
        return jsonify({
            "message": "Persona saved successfully",
            "filename": filename,
            "filepath": filepath
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Modified route for displaying personas
@app.route("/display-personas", methods=["GET"])
def display_personas_api():
    """Get all personas from the personas directory for display in focus-group"""
    try:
        personas_dir = "personas"
        if not os.path.exists(personas_dir):
            return jsonify([])
        
        personas = []
        for filename in os.listdir(personas_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(personas_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        persona_data = json.load(f)
                        # Ensure the persona has an id field (use filename without extension as id)
                        persona_id = filename.replace('.json', '')
                        persona_data['id'] = persona_id
                        
                        # Ensure required fields exist with defaults
                        if 'traits' not in persona_data:
                            persona_data['traits'] = [persona_data.get('description', 'General')]
                        
                        personas.append(persona_data)
                except json.JSONDecodeError:
                    app.logger.warning(f"Could not parse JSON from {filename}")
                    continue
        
        return jsonify(personas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/api/saved-personas", methods=["GET"])
def get_saved_personas():
    """Get all saved personas from the personas directory"""
    try:
        personas_dir = "personas"
        if not os.path.exists(personas_dir):
            return jsonify([])
        
        personas = []
        for filename in os.listdir(personas_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(personas_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        persona_data = json.load(f)
                        # Add filename to the persona data
                        persona_data['filename'] = filename
                        personas.append(persona_data)
                except json.JSONDecodeError:
                    app.logger.warning(f"Could not parse JSON from {filename}")
                    continue
        
        return jsonify(personas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/delete-persona/<filename>", methods=["DELETE"])
def delete_persona(filename):
    """Delete a specific persona file"""
    try:
        personas_dir = "personas"
        filepath = os.path.join(personas_dir, filename)
        
        # Security check: ensure the file is within the personas directory
        if not os.path.abspath(filepath).startswith(os.path.abspath(personas_dir)):
            return jsonify({"error": "Invalid file path"}), 400
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"message": f"Persona {filename} deleted successfully"}), 200
        else:
            return jsonify({"error": "Persona file not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
