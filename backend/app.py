import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Allow requests from your frontend development server (DEBUGGING - VERY PERMISSIVE)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def index():
    return "Hello, World!"

# All persona generation and file upload logic has been removed.
# You can add new endpoints here in the future.

if __name__ == "__main__":
    app.run(debug=True)
