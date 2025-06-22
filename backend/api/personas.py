from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError
from services.persona_service import PersonaService
from core.exceptions import PersonaError, ValidationError as CoreValidationError
from core.logging import api_logger
import traceback

# Create blueprint
personas_bp = Blueprint('personas', __name__)

# Validation schemas
class PersonaTraitsSchema(Schema):
    """Schema for persona traits validation"""
    curiosity = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)
    optimism = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)
    assertiveness = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)
    empathy = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)
    analytical = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)
    creativity = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)

class PersonaCreateSchema(Schema):
    """Schema for creating personas"""
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    avatar = fields.Str(missing="🤖")
    personality_traits = fields.Nested(PersonaTraitsSchema, missing=dict)
    communication_style = fields.Str(missing="friendly")
    background_context = fields.Str(missing="")
    expertise_areas = fields.List(fields.Str(), missing=list)
    sentiment_bias = fields.Float(validate=lambda x: -1 <= x <= 1, missing=0.0)
    engagement_level = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.7)
    controversy_tolerance = fields.Float(validate=lambda x: 0 <= x <= 1, missing=0.5)

class PersonaUpdateSchema(Schema):
    """Schema for updating personas (all fields optional)"""
    name = fields.Str(validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(validate=lambda x: len(x.strip()) > 0)
    avatar = fields.Str()
    personality_traits = fields.Nested(PersonaTraitsSchema)
    communication_style = fields.Str()
    background_context = fields.Str()
    expertise_areas = fields.List(fields.Str())
    sentiment_bias = fields.Float(validate=lambda x: -1 <= x <= 1)
    engagement_level = fields.Float(validate=lambda x: 0 <= x <= 1)
    controversy_tolerance = fields.Float(validate=lambda x: 0 <= x <= 1)

# Initialize schemas
persona_create_schema = PersonaCreateSchema()
persona_update_schema = PersonaUpdateSchema()

@personas_bp.route('', methods=['GET'])
def list_personas():
    """List all personas with optional filtering"""
    try:
        # Get query parameters
        include_default = request.args.get('include_default', 'true').lower() == 'true'
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        creator_id = request.args.get('creator_id')
        
        # Get personas from service
        persona_service = PersonaService()
        personas = persona_service.get_all_personas(
            include_default=include_default,
            active_only=active_only,
            creator_id=creator_id
        )
        
        # Convert to frontend-compatible format
        personas_data = [persona.to_frontend_dict() for persona in personas]
        
        api_logger.info(f"Listed {len(personas_data)} personas", 
                       include_default=include_default, active_only=active_only)
        
        return jsonify({
            'success': True,
            'data': personas_data,
            'count': len(personas_data)
        })
        
    except Exception as e:
        api_logger.error(f"Error listing personas: {str(e)}", 
                        error=str(e), traceback=traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to list personas',
            'message': str(e)
        }), 500

@personas_bp.route('/<persona_id>', methods=['GET'])
def get_persona(persona_id):
    """Get a specific persona by ID"""
    try:
        persona_service = PersonaService()
        persona = persona_service.get_persona(persona_id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona not found',
                'message': f'No persona found with ID: {persona_id}'
            }), 404
        
        api_logger.info(f"Retrieved persona: {persona.name}", persona_id=persona_id)
        
        return jsonify({
            'success': True,
            'data': persona.to_frontend_dict()
        })
        
    except PersonaError as e:
        return jsonify({
            'success': False,
            'error': 'Persona error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        api_logger.error(f"Error getting persona {persona_id}: {str(e)}", 
                        persona_id=persona_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get persona',
            'message': str(e)
        }), 500

@personas_bp.route('', methods=['POST'])
def create_persona():
    """Create a new persona"""
    try:
        # Validate request data
        try:
            data = persona_create_schema.load(request.json)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'message': 'Invalid persona data',
                'details': e.messages
            }), 400
        
        # Create persona
        persona_service = PersonaService()
        persona = persona_service.create_persona(data)
        
        api_logger.info(f"Created persona: {persona.name}", persona_id=persona.id)
        
        return jsonify({
            'success': True,
            'data': persona.to_frontend_dict(),
            'message': f'Persona "{persona.name}" created successfully'
        }), 201
        
    except PersonaError as e:
        return jsonify({
            'success': False,
            'error': 'Persona error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        api_logger.error(f"Error creating persona: {str(e)}", 
                        error=str(e), data=request.json)
        return jsonify({
            'success': False,
            'error': 'Failed to create persona',
            'message': str(e)
        }), 500

@personas_bp.route('/<persona_id>', methods=['PUT'])
def update_persona(persona_id):
    """Update an existing persona"""
    try:
        # Validate request data
        try:
            data = persona_update_schema.load(request.json)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Validation error',
                'message': 'Invalid persona data',
                'details': e.messages
            }), 400
        
        # Update persona
        persona_service = PersonaService()
        persona = persona_service.update_persona(persona_id, data)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona not found',
                'message': f'No persona found with ID: {persona_id}'
            }), 404
        
        api_logger.info(f"Updated persona: {persona.name}", persona_id=persona_id)
        
        return jsonify({
            'success': True,
            'data': persona.to_frontend_dict(),
            'message': f'Persona "{persona.name}" updated successfully'
        })
        
    except PersonaError as e:
        return jsonify({
            'success': False,
            'error': 'Persona error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        api_logger.error(f"Error updating persona {persona_id}: {str(e)}", 
                        persona_id=persona_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to update persona',
            'message': str(e)
        }), 500

@personas_bp.route('/<persona_id>', methods=['DELETE'])
def delete_persona(persona_id):
    """Delete a persona (soft delete)"""
    try:
        persona_service = PersonaService()
        success = persona_service.delete_persona(persona_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Persona not found',
                'message': f'No persona found with ID: {persona_id}'
            }), 404
        
        api_logger.info(f"Deleted persona", persona_id=persona_id)
        
        return jsonify({
            'success': True,
            'message': 'Persona deleted successfully'
        })
        
    except PersonaError as e:
        return jsonify({
            'success': False,
            'error': 'Persona error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        api_logger.error(f"Error deleting persona {persona_id}: {str(e)}", 
                        persona_id=persona_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to delete persona',
            'message': str(e)
        }), 500

@personas_bp.route('/defaults', methods=['POST'])
def create_default_personas():
    """Create/reset default personas"""
    try:
        persona_service = PersonaService()
        personas = persona_service.create_default_personas()
        
        api_logger.info(f"Created {len(personas)} default personas")
        
        return jsonify({
            'success': True,
            'data': [persona.to_frontend_dict() for persona in personas],
            'message': f'Created {len(personas)} default personas'
        })
        
    except Exception as e:
        api_logger.error(f"Error creating default personas: {str(e)}", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to create default personas',
            'message': str(e)
        }), 500

@personas_bp.route('/<persona_id>/activate', methods=['POST'])
def activate_persona(persona_id):
    """Activate a persona"""
    try:
        persona_service = PersonaService()
        persona = persona_service.activate_persona(persona_id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona not found',
                'message': f'No persona found with ID: {persona_id}'
            }), 404
        
        api_logger.info(f"Activated persona: {persona.name}", persona_id=persona_id)
        
        return jsonify({
            'success': True,
            'data': persona.to_frontend_dict(),
            'message': f'Persona "{persona.name}" activated'
        })
        
    except Exception as e:
        api_logger.error(f"Error activating persona {persona_id}: {str(e)}", 
                        persona_id=persona_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to activate persona',
            'message': str(e)
        }), 500

@personas_bp.route('/<persona_id>/deactivate', methods=['POST'])
def deactivate_persona(persona_id):
    """Deactivate a persona"""
    try:
        persona_service = PersonaService()
        persona = persona_service.deactivate_persona(persona_id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona not found',
                'message': f'No persona found with ID: {persona_id}'
            }), 404
        
        api_logger.info(f"Deactivated persona: {persona.name}", persona_id=persona_id)
        
        return jsonify({
            'success': True,
            'data': persona.to_frontend_dict(),
            'message': f'Persona "{persona.name}" deactivated'
        })
        
    except Exception as e:
        api_logger.error(f"Error deactivating persona {persona_id}: {str(e)}", 
                        persona_id=persona_id, error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to deactivate persona',
            'message': str(e)
        }), 500 