from .base import db, BaseModel
from sqlalchemy.dialects.postgresql import JSON
import json

class Persona(BaseModel):
    """Persona model for storing AI persona definitions"""
    __tablename__ = 'personas'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.String(255), default='👤')
    
    # Persona characteristics
    personality_traits = db.Column(JSON)  # JSON field for flexible trait storage
    communication_style = db.Column(db.Text)
    background_context = db.Column(db.Text)
    expertise_areas = db.Column(JSON)  # List of expertise areas
    
    # Behavioral parameters
    sentiment_bias = db.Column(db.Float, default=0.0)  # -1.0 to 1.0
    engagement_level = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    controversy_tolerance = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    
    # Metadata
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    creator_id = db.Column(db.String(36))  # For user-created personas
    
    # Relationships
    traits = db.relationship('PersonaTrait', backref='persona', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Persona {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary with relationships"""
        result = super().to_dict()
        result['traits'] = [trait.to_dict() for trait in self.traits]
        return result
    
    def to_frontend_dict(self):
        """Convert to frontend-compatible format"""
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'description': self.description,
            'traits': self.expertise_areas or []  # Frontend expects traits as string array
        }
    
    def get_trait_value(self, trait_name):
        """Get the value of a specific trait"""
        trait = self.traits.filter_by(name=trait_name).first()
        return trait.value if trait else None
    
    def set_trait_value(self, trait_name, value, description=None):
        """Set or update a trait value"""
        trait = self.traits.filter_by(name=trait_name).first()
        if trait:
            trait.value = value
            if description:
                trait.description = description
        else:
            trait = PersonaTrait(
                persona_id=self.id,
                name=trait_name,
                value=value,
                description=description
            )
            db.session.add(trait)
        return trait
    
    @classmethod
    def get_default_personas(cls):
        """Get all default personas"""
        return cls.query.filter_by(is_default=True, is_active=True).all()
    
    @classmethod
    def get_by_creator(cls, creator_id):
        """Get personas created by a specific user"""
        return cls.query.filter_by(creator_id=creator_id, is_active=True).all()

class PersonaTrait(BaseModel):
    """Individual traits for personas"""
    __tablename__ = 'persona_traits'
    
    persona_id = db.Column(db.String(36), db.ForeignKey('personas.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)  # Normalized value 0.0 to 1.0
    description = db.Column(db.Text)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('persona_id', 'name', name='_persona_trait_uc'),)
    
    def __repr__(self):
        return f'<PersonaTrait {self.name}: {self.value}>' 