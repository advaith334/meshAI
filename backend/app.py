import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
# Allow requests from your frontend development server (DEBUGGING - VERY PERMISSIVE)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/save-persona", methods=['POST'])
def save_persona():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Sanitize filename and ensure directory exists
    filename = "".join(x for x in name if x.isalnum() or x in " _-").rstrip()
    os.makedirs('personas', exist_ok=True)
    filepath = os.path.join('personas', f"{filename}.json")

    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({"success": True, "message": f"Persona '{name}' saved."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Hello, World!"

# All persona generation and file upload logic has been removed.
# You can add new endpoints here in the future.

if __name__ == "__main__":
    app.run(debug=True)
