from typing import List, Dict, Any, Optional
from models.persona import Persona, PersonaTrait
from models.base import db
from core.logging import db_logger
from core.exceptions import PersonaError, ValidationError

class PersonaService:
    """Service for managing personas and their traits"""
    
    def __init__(self):
        self.logger = db_logger
    
    def create_default_personas(self):
        """Create default personas if they don't exist"""
        default_personas_data = [
            {
                'name': 'Tech Enthusiast',
                'description': 'Always excited about the latest innovations and gadgets',
                'avatar': '🤖',
                'personality_traits': {
                    'curiosity': 0.9,
                    'optimism': 0.8,
                    'analytical': 0.7,
                    'early_adopter': 0.9
                },
                'communication_style': 'Enthusiastic and technical, often uses industry jargon',
                'background_context': 'Works in tech industry, follows latest trends and innovations',
                'expertise_areas': ['technology', 'innovation', 'gadgets', 'software'],
                'sentiment_bias': 0.3,
                'engagement_level': 0.8,
                'controversy_tolerance': 0.6
            },
            {
                'name': 'Price-Sensitive Shopper',
                'description': 'Focused on value and getting the best deals',
                'avatar': '💰',
                'personality_traits': {
                    'frugality': 0.9,
                    'analytical': 0.8,
                    'skepticism': 0.7,
                    'patience': 0.8
                },
                'communication_style': 'Practical and detail-oriented, asks about costs and value',
                'background_context': 'Budget-conscious consumer who researches thoroughly before purchases',
                'expertise_areas': ['budgeting', 'comparison shopping', 'deals', 'value analysis'],
                'sentiment_bias': -0.1,
                'engagement_level': 0.6,
                'controversy_tolerance': 0.4
            },
            {
                'name': 'Eco-Conscious Consumer',
                'description': 'Prioritizes sustainability and environmental impact',
                'avatar': '🌱',
                'personality_traits': {
                    'environmental_awareness': 0.9,
                    'responsibility': 0.8,
                    'idealism': 0.7,
                    'activism': 0.6
                },
                'communication_style': 'Passionate about sustainability, often mentions environmental impact',
                'background_context': 'Environmentally conscious individual who makes purchasing decisions based on sustainability',
                'expertise_areas': ['sustainability', 'environment', 'green products', 'climate change'],
                'sentiment_bias': 0.1,
                'engagement_level': 0.7,
                'controversy_tolerance': 0.8
            },
            {
                'name': 'Early Adopter',
                'description': 'First to try new products and trends',
                'avatar': '🚀',
                'personality_traits': {
                    'risk_taking': 0.8,
                    'curiosity': 0.9,
                    'influence': 0.7,
                    'trendsetting': 0.8
                },
                'communication_style': 'Confident and forward-thinking, often shares experiences with new products',
                'background_context': 'Trend-conscious individual who enjoys being first to try new things',
                'expertise_areas': ['trends', 'innovation', 'new products', 'early adoption'],
                'sentiment_bias': 0.4,
                'engagement_level': 0.9,
                'controversy_tolerance': 0.7
            },
            {
                'name': 'Skeptical Buyer',
                'description': 'Cautious and requires convincing before making decisions',
                'avatar': '🤔',
                'personality_traits': {
                    'skepticism': 0.9,
                    'caution': 0.8,
                    'analytical': 0.8,
                    'risk_aversion': 0.7
                },
                'communication_style': 'Questions claims, asks for evidence, expresses doubts and concerns',
                'background_context': 'Careful consumer who has been disappointed by products before',
                'expertise_areas': ['critical thinking', 'risk assessment', 'product evaluation'],
                'sentiment_bias': -0.3,
                'engagement_level': 0.5,
                'controversy_tolerance': 0.3
            }
        ]
        
        created_personas = []
        for persona_data in default_personas_data:
            existing = Persona.query.filter_by(name=persona_data['name'], is_default=True).first()
            if not existing:
                persona = self.create_persona(persona_data, is_default=True)
                created_personas.append(persona)
                self.logger.info(f"Created default persona: {persona_data['name']}")
            else:
                created_personas.append(existing)
        
        return created_personas
    
    def create_persona(self, persona_data: Dict[str, Any], is_default: bool = False) -> Persona:
        """Create a new persona"""
        try:
            # Validate required fields
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in persona_data or not persona_data[field]:
                    raise ValidationError(f"Missing required field: {field}", field=field)
            
            # Create persona
            persona = Persona(
                name=persona_data['name'],
                description=persona_data['description'],
                avatar=persona_data.get('avatar', '👤'),
                personality_traits=persona_data.get('personality_traits'),
                communication_style=persona_data.get('communication_style'),
                background_context=persona_data.get('background_context'),
                expertise_areas=persona_data.get('expertise_areas'),
                sentiment_bias=persona_data.get('sentiment_bias', 0.0),
                engagement_level=persona_data.get('engagement_level', 0.5),
                controversy_tolerance=persona_data.get('controversy_tolerance', 0.5),
                is_default=is_default,
                creator_id=persona_data.get('creator_id')
            )
            
            persona.save()
            
            # Create individual traits if provided
            if 'traits' in persona_data:
                for trait_name, trait_value in persona_data['traits'].items():
                    persona.set_trait_value(trait_name, trait_value)
            
            self.logger.info(f"Created persona: {persona.name}", persona_id=persona.id)
            return persona
            
        except Exception as e:
            self.logger.error(f"Error creating persona: {str(e)}")
            raise PersonaError(f"Failed to create persona: {str(e)}")
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get a persona by ID"""
        try:
            persona = Persona.get_by_id(persona_id)
            if not persona or not persona.is_active:
                return None
            return persona
        except Exception as e:
            self.logger.error(f"Error getting persona {persona_id}: {str(e)}")
            raise PersonaError(f"Failed to get persona: {str(e)}", persona_id=persona_id)
    
    def get_all_personas(self, include_default: bool = True, active_only: bool = True, creator_id: str = None) -> List[Persona]:
        """Get all personas with filtering options"""
        try:
            query = Persona.query
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            if not include_default:
                query = query.filter_by(is_default=False)
            
            if creator_id:
                query = query.filter_by(creator_id=creator_id)
            
            return query.all()
        except Exception as e:
            self.logger.error(f"Error getting personas: {str(e)}")
            raise PersonaError(f"Failed to get personas: {str(e)}")
    
    def get_default_personas(self) -> List[Persona]:
        """Get all default personas"""
        try:
            return Persona.get_default_personas()
        except Exception as e:
            self.logger.error(f"Error getting default personas: {str(e)}")
            raise PersonaError(f"Failed to get default personas: {str(e)}")
    
    def update_persona(self, persona_id: str, update_data: Dict[str, Any]) -> Persona:
        """Update a persona"""
        try:
            persona = self.get_persona(persona_id)
            if not persona:
                raise PersonaError(f"Persona not found", persona_id=persona_id)
            
            # Don't allow updating default personas
            if persona.is_default:
                raise PersonaError("Cannot update default personas", persona_id=persona_id)
            
            # Update fields
            updatable_fields = [
                'name', 'description', 'avatar', 'personality_traits',
                'communication_style', 'background_context', 'expertise_areas',
                'sentiment_bias', 'engagement_level', 'controversy_tolerance'
            ]
            
            for field in updatable_fields:
                if field in update_data:
                    setattr(persona, field, update_data[field])
            
            persona.save()
            
            # Update individual traits if provided
            if 'traits' in update_data:
                for trait_name, trait_value in update_data['traits'].items():
                    persona.set_trait_value(trait_name, trait_value)
            
            self.logger.info(f"Updated persona: {persona.name}", persona_id=persona.id)
            return persona
            
        except PersonaError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating persona {persona_id}: {str(e)}")
            raise PersonaError(f"Failed to update persona: {str(e)}", persona_id=persona_id)
    
    def delete_persona(self, persona_id: str) -> bool:
        """Soft delete a persona"""
        try:
            persona = self.get_persona(persona_id)
            if not persona:
                raise PersonaError(f"Persona not found", persona_id=persona_id)
            
            # Don't allow deleting default personas
            if persona.is_default:
                raise PersonaError("Cannot delete default personas", persona_id=persona_id)
            
            persona.is_active = False
            persona.save()
            
            self.logger.info(f"Deleted persona: {persona.name}", persona_id=persona.id)
            return True
            
        except PersonaError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting persona {persona_id}: {str(e)}")
            raise PersonaError(f"Failed to delete persona: {str(e)}", persona_id=persona_id)
    
    def get_personas_by_ids(self, persona_ids: List[str]) -> List[Persona]:
        """Get multiple personas by their IDs"""
        try:
            personas = []
            for persona_id in persona_ids:
                persona = self.get_persona(persona_id)
                if persona:
                    personas.append(persona)
            return personas
        except Exception as e:
            self.logger.error(f"Error getting personas by IDs: {str(e)}")
            raise PersonaError(f"Failed to get personas: {str(e)}")
    
    def search_personas(self, query: str, limit: int = 10) -> List[Persona]:
        """Search personas by name or description"""
        try:
            search_term = f"%{query}%"
            personas = Persona.query.filter(
                db.and_(
                    Persona.is_active == True,
                    db.or_(
                        Persona.name.ilike(search_term),
                        Persona.description.ilike(search_term)
                    )
                )
            ).limit(limit).all()
            
            return personas
        except Exception as e:
            self.logger.error(f"Error searching personas: {str(e)}")
            raise PersonaError(f"Failed to search personas: {str(e)}")
    
    def activate_persona(self, persona_id: str) -> Optional[Persona]:
        """Activate a persona"""
        try:
            persona = Persona.get_by_id(persona_id)
            if not persona:
                return None
            
            persona.is_active = True
            persona.save()
            
            self.logger.info(f"Activated persona: {persona.name}", persona_id=persona.id)
            return persona
            
        except Exception as e:
            self.logger.error(f"Error activating persona {persona_id}: {str(e)}")
            raise PersonaError(f"Failed to activate persona: {str(e)}", persona_id=persona_id)
    
    def deactivate_persona(self, persona_id: str) -> Optional[Persona]:
        """Deactivate a persona"""
        try:
            persona = Persona.get_by_id(persona_id)
            if not persona:
                return None
            
            # Don't allow deactivating default personas
            if persona.is_default:
                raise PersonaError("Cannot deactivate default personas", persona_id=persona_id)
            
            persona.is_active = False
            persona.save()
            
            self.logger.info(f"Deactivated persona: {persona.name}", persona_id=persona.id)
            return persona
            
        except PersonaError:
            raise
        except Exception as e:
            self.logger.error(f"Error deactivating persona {persona_id}: {str(e)}")
            raise PersonaError(f"Failed to deactivate persona: {str(e)}", persona_id=persona_id) 