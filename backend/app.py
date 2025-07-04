import os
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from crew_manager import CrewManager
from crewai import Crew, Process
from datetime import datetime

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
                
                # Get persona info from JSON data instead of agents_config
                if hasattr(crew_manager, '_personas_from_json') and persona_id in crew_manager._personas_from_json:
                    persona_name = crew_manager._personas_from_json[persona_id]['role']
                else:
                    # Fallback to agents_config
                    persona_config = crew_manager.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                initial_reactions.append({
                    "id": crew_manager._generate_uuid(),
                    "persona_id": persona_id,
                    "persona_name": persona_name.strip(),  # Remove newlines
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
                
                # Get persona info from JSON data instead of agents_config
                if hasattr(crew_manager, '_personas_from_json') and persona_id in crew_manager._personas_from_json:
                    persona_name = crew_manager._personas_from_json[persona_id]['role']
                else:
                    # Fallback to agents_config
                    persona_config = crew_manager.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                round_messages.append({
                    "id": crew_manager._generate_uuid(),
                    "persona_id": persona_id,
                    "persona_name": persona_name.strip(),  # Remove newlines
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

@app.route("/api/save-session", methods=["POST"])
def save_session():
    """Save session data (interview or focus group) to JSON file"""
    try:
        data = request.json
        
        # Create prev_prompts directory if it doesn't exist
        prev_prompts_dir = "prev_prompts"
        if not os.path.exists(prev_prompts_dir):
            os.makedirs(prev_prompts_dir)
        
        # Generate filename with timestamp
        import time
        timestamp = int(time.time())
        session_type = data.get("session_type", "unknown")
        session_name = data.get("session_name", "session")
        
        # Sanitize session name for filename
        safe_name = "".join(c for c in session_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        filename = f"{session_type}_{safe_name}_{timestamp}.json"
        filepath = os.path.join(prev_prompts_dir, filename)
        
        # Enhance persona data with names and avatars
        enhanced_personas = []
        if "selected_personas" in data:
            personas_dir = "personas"
            if os.path.exists(personas_dir):
                for persona_id in data["selected_personas"]:
                    persona_file = f"{persona_id}.json"
                    persona_path = os.path.join(personas_dir, persona_file)
                    if os.path.exists(persona_path):
                        try:
                            with open(persona_path, 'r') as pf:
                                persona_data = json.load(pf)
                                enhanced_personas.append({
                                    "id": persona_id,
                                    "name": persona_data.get("name", "Unknown"),
                                    "role": persona_data.get("role", "Unknown Role"),
                                    "avatar": persona_data.get("avatar", "👤"),
                                    "description": persona_data.get("description", "")
                                })
                        except:
                            enhanced_personas.append({
                                "id": persona_id,
                                "name": "Unknown",
                                "role": "Unknown Role",
                                "avatar": "👤",
                                "description": ""
                            })
                    else:
                        enhanced_personas.append({
                            "id": persona_id,
                            "name": "Unknown",
                            "role": "Unknown Role",
                            "avatar": "👤",
                            "description": ""
                        })
        
        # Add metadata
        session_data = {
            "metadata": {
                "session_type": session_type,
                "session_name": session_name,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "duration_seconds": data.get("duration", 0)
            },
            "session_data": {
                **data,
                "enhanced_personas": enhanced_personas
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=4)
        
        app.logger.info(f"Session saved: {filepath}")
        
        return jsonify({
            "message": "Session saved successfully",
            "filename": filename,
            "filepath": filepath
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error saving session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/get-sessions", methods=["GET"])
def get_sessions():
    """Get all saved sessions"""
    try:
        prev_prompts_dir = "prev_prompts"
        if not os.path.exists(prev_prompts_dir):
            return jsonify([])
        
        sessions = []
        for filename in os.listdir(prev_prompts_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(prev_prompts_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                        sessions.append({
                            "filename": filename,
                            "metadata": session_data.get("metadata", {}),
                            "session_data": session_data.get("session_data", {})
                        })
                except json.JSONDecodeError:
                    app.logger.warning(f"Could not parse JSON from {filename}")
                    continue
        
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x["metadata"].get("timestamp", 0), reverse=True)
        
        return jsonify(sessions)
        
    except Exception as e:
        app.logger.error(f"Error getting sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard-sessions", methods=["GET"])
def get_dashboard_sessions():
    """Get session data for dashboard overview"""
    try:
        prev_prompts_dir = "prev_prompts"
        if not os.path.exists(prev_prompts_dir):
            return jsonify([])
        
        sessions = []
        for filename in os.listdir(prev_prompts_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(prev_prompts_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                        metadata = session_data.get("metadata", {})
                        session_info = session_data.get("session_data", {})
                        
                        # Extract persona avatars from enhanced_personas if available
                        persona_avatars = []
                        if "enhanced_personas" in session_info:
                            persona_avatars = [p.get("avatar", "👤") for p in session_info["enhanced_personas"]]
                        elif "selected_personas" in session_info:
                            # Fallback to loading from personas directory
                            personas_dir = "personas"
                            if os.path.exists(personas_dir):
                                for persona_id in session_info["selected_personas"]:
                                    persona_file = f"{persona_id}.json"
                                    persona_path = os.path.join(personas_dir, persona_file)
                                    if os.path.exists(persona_path):
                                        try:
                                            with open(persona_path, 'r') as pf:
                                                persona_data = json.load(pf)
                                                persona_avatars.append(persona_data.get("avatar", "👤"))
                                        except:
                                            persona_avatars.append("👤")
                                    else:
                                        persona_avatars.append("👤")
                        
                        sessions.append({
                            "id": filename.replace('.json', ''),
                            "name": metadata.get("session_name", "Unknown Session"),
                            "session_type": metadata.get("session_type", "unknown"),
                            "persona_avatars": persona_avatars,
                            "start_date": metadata.get("created_at", ""),
                            "duration": metadata.get("duration_seconds", 0),
                            "status": "Completed"  # All saved sessions are completed
                        })
                except json.JSONDecodeError:
                    app.logger.warning(f"Could not parse JSON from {filename}")
                    continue
        
        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x.get("start_date", ""), reverse=True)
        
        return jsonify(sessions)
        
    except Exception as e:
        app.logger.error(f"Error getting dashboard sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-insights", methods=["POST"])
def generate_insights():
    """Generate insights using Gemini AI based on conversation data"""
    try:
        data = request.json
        session_data = data.get("session_data", {})
        
        # Extract conversation messages
        messages = session_data.get("messages", [])
        purpose = session_data.get("purpose", "")
        session_type = session_data.get("session_type", "")
        
        if not messages:
            return jsonify({"error": "No conversation data provided"}), 400
        
        # Create a prompt for Gemini to analyze the conversation
        conversation_text = ""
        for msg in messages:
            sender = "Interviewer" if msg.get("sender") == "user" else "Persona"
            content = msg.get("content", "")
            conversation_text += f"{sender}: {content}\n\n"
        
        prompt = f"""
        Analyze this {session_type} conversation and provide 8 key insights in point form. 
        The purpose of this session was: {purpose}
        
        Conversation:
        {conversation_text}
        
        Please provide 8 specific, actionable insights based on this conversation. Focus on:
        1. Key themes and patterns
        2. Important concerns or pain points
        3. Positive feedback and suggestions
        4. Market opportunities
        5. Areas for improvement
        6. Competitive insights
        7. User needs and preferences
        8. Strategic recommendations
        
        Format each insight as a clear, concise point starting with a capital letter and ending with a period.
        """
        
        # Use CrewManager to generate insights with Gemini
        try:
            # Create a simple agent for insight generation
            agent = crew_manager.create_agent("insight_analyzer")
            if not agent:
                # Fallback to direct LLM call
                from crewai import LLM
                llm = LLM(
                    model="gemini/gemini-2.5-flash",
                    google_api_key=gemini_api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
                response = llm.complete(prompt)
                insights_text = str(response)
            else:
                # Use CrewAI task
                task = crew_manager.create_task(
                    'insight_generation_task',
                    agent,
                    prompt=prompt
                )
                if task:
                    crew = Crew(
                        agents=[agent],
                        tasks=[task],
                        process=Process.sequential,
                        verbose=False
                    )
                    result = crew.kickoff()
                    insights_text = str(result)
                else:
                    return jsonify({"error": "Failed to create insight generation task"}), 500
            
            # Parse the response into individual insights
            insights = []
            lines = insights_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line[0].isdigit() or line[0].isupper()):
                    # Clean up the line
                    clean_line = line.lstrip('•-1234567890. ')
                    if clean_line and len(clean_line) > 10:  # Ensure it's a substantial insight
                        insights.append(clean_line)
            
            # If we don't have enough insights, create some fallback ones
            if len(insights) < 4:
                insights = [
                    "The persona demonstrated strong interest in user experience and design principles",
                    "Key concerns were raised about scalability and technical implementation",
                    "Positive feedback was given regarding the innovative approach to problem-solving",
                    "The conversation revealed potential market opportunities in the target demographic",
                    "Several actionable suggestions were provided for feature improvements",
                    "The persona showed deep understanding of industry challenges and pain points",
                    "Important questions were raised about pricing strategy and competitive positioning",
                    "The discussion highlighted areas where the product could differentiate itself"
                ]
            
            # Limit to 8 insights
            insights = insights[:8]
            
            return jsonify({
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"Error generating insights with Gemini: {e}")
            # Fallback insights
            fallback_insights = [
                "The persona demonstrated strong interest in user experience and design principles",
                "Key concerns were raised about scalability and technical implementation",
                "Positive feedback was given regarding the innovative approach to problem-solving",
                "The conversation revealed potential market opportunities in the target demographic",
                "Several actionable suggestions were provided for feature improvements",
                "The persona showed deep understanding of industry challenges and pain points",
                "Important questions were raised about pricing strategy and competitive positioning",
                "The discussion highlighted areas where the product could differentiate itself"
            ]
            return jsonify({
                "insights": fallback_insights,
                "generated_at": datetime.now().isoformat(),
                "note": "Fallback insights generated due to AI processing error"
            })
        
    except Exception as e:
        app.logger.error(f"Error in generate-insights: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
