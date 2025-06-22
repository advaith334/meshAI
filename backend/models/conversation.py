from .base import db, BaseModel
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class Conversation(BaseModel):
    """Conversation model for storing chat sessions"""
    __tablename__ = 'conversations'
    
    title = db.Column(db.String(200))
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    persona_id = db.Column(db.String(36), db.ForeignKey('personas.id'), nullable=False)
    user_id = db.Column(db.String(36))  # Optional user tracking
    
    # Conversation metadata
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    context = db.Column(JSON)  # Store conversation context/memory
    total_messages = db.Column(db.Integer, default=0)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    persona = db.relationship('Persona', backref='conversations')
    
    def __repr__(self):
        return f'<Conversation {self.session_id}>'
    
    def to_dict(self):
        """Convert to dictionary with relationships"""
        result = super().to_dict()
        result['persona'] = self.persona.to_dict() if self.persona else None
        result['message_count'] = self.messages.count()
        result['last_message_at'] = None
        
        last_message = self.messages.order_by(Message.created_at.desc()).first()
        if last_message:
            result['last_message_at'] = last_message.created_at.isoformat()
        
        return result
    
    def add_message(self, content, sender='user', metadata=None):
        """Add a message to the conversation"""
        message = Message(
            conversation_id=self.id,
            content=content,
            sender=sender,
            message_metadata=metadata or {}
        )
        db.session.add(message)
        
        # Update message count
        self.total_messages = self.messages.count() + 1
        self.updated_at = datetime.utcnow()
        
        db.session.commit()
        return message
    
    def get_messages(self, limit=None, offset=0):
        """Get messages with optional pagination"""
        query = self.messages.order_by(Message.created_at.asc())
        if limit:
            query = query.offset(offset).limit(limit)
        return query.all()
    
    def get_context_summary(self):
        """Get a summary of the conversation for context"""
        recent_messages = self.messages.order_by(Message.created_at.desc()).limit(10).all()
        return {
            'total_messages': self.total_messages,
            'recent_messages': [msg.to_dict() for msg in reversed(recent_messages)],
            'context': self.context or {}
        }

class Message(BaseModel):
    """Message model for individual chat messages"""
    __tablename__ = 'messages'
    
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'persona'
    
    # Message metadata
    message_metadata = db.Column(JSON)  # Store additional message data
    sentiment_score = db.Column(db.Float)  # Analyzed sentiment
    processing_time = db.Column(db.Float)  # Time taken to generate response
    token_count = db.Column(db.Integer)  # Token usage tracking
    
    # Message status
    is_edited = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Message {self.id[:8]}... from {self.sender}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        result = super().to_dict()
        if self.is_deleted:
            result['content'] = '[Message deleted]'
        return result
    
    @classmethod
    def get_by_conversation(cls, conversation_id, include_deleted=False):
        """Get messages for a conversation"""
        query = cls.query.filter_by(conversation_id=conversation_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.order_by(cls.created_at.asc()).all()
    
    def mark_deleted(self):
        """Soft delete a message"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_content(self, new_content):
        """Update message content"""
        self.content = new_content
        self.is_edited = True
        self.updated_at = datetime.utcnow()
        db.session.commit() 