import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Import our core modules
from config import config, Config
from core.container import setup_container
from core.logging import setup_logging
from core.exceptions import MeshAIException
from models import db

# Import API blueprints
from api.personas import personas_bp
from api.conversations import conversations_bp
# from api.focus_groups import focus_groups_bp

load_dotenv()

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Determine config
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app_config = config.get(config_name, config['default'])
    
    # Validate configuration
    try:
        app_config.validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your environment variables.")
        exit(1)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(app_config)
    
    # Setup logging
    setup_logging(app_config)
    
    # Setup dependency injection container
    container = setup_container(app_config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/*": {
            "origins": app_config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Setup SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins=app_config.CORS_ORIGINS)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default personas if they don't exist
        from services.persona_service import PersonaService
        persona_service = PersonaService()
        persona_service.create_default_personas()
    
    return app, socketio

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(MeshAIException)
    def handle_meshai_exception(error):
        """Handle custom MeshAI exceptions"""
        return jsonify(error.to_dict()), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': True,
            'message': 'Resource not found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'error': True,
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

def register_blueprints(app):
    """Register API blueprints"""
    
    # Health check endpoint
    @app.route("/")
    def index():
        return jsonify({
            'status': 'healthy',
            'message': 'MeshAI Backend API',
            'version': '1.0.0'
        })
    
    @app.route("/health")
    def health_check():
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    
    # Register API blueprints
    app.register_blueprint(personas_bp, url_prefix='/api/personas')
    app.register_blueprint(conversations_bp, url_prefix='/api')
    
    # Register API blueprints when they're created
    # app.register_blueprint(focus_groups_bp, url_prefix='/api/focus-groups')

# Create the application
app, socketio = create_app()

if __name__ == "__main__":
    # Run with SocketIO support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
