from .base import db, BaseModel
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class FocusGroup(BaseModel):
    """Focus group model for multi-persona discussions"""
    __tablename__ = 'focus_groups'
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    initial_question = db.Column(db.Text, nullable=False)
    
    # Group configuration
    max_rounds = db.Column(db.Integer, default=3)
    current_round = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='created')  # created, active, completed, paused
    
    # Group settings
    settings = db.Column(JSON)  # Store group configuration
    user_id = db.Column(db.String(36))  # Optional user tracking
    
    # Relationships
    participants = db.relationship('FocusGroupParticipant', backref='focus_group', lazy='dynamic', cascade='all, delete-orphan')
    rounds = db.relationship('FocusGroupRound', backref='focus_group', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FocusGroup {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary with relationships"""
        result = super().to_dict()
        result['participant_count'] = self.participants.count()
        result['participants'] = [p.to_dict() for p in self.participants]
        result['rounds_data'] = [r.to_dict() for r in self.rounds.order_by(FocusGroupRound.round_number)]
        return result
    
    def add_participant(self, persona_id, role='participant'):
        """Add a persona to the focus group"""
        participant = FocusGroupParticipant(
            focus_group_id=self.id,
            persona_id=persona_id,
            role=role
        )
        db.session.add(participant)
        db.session.commit()
        return participant
    
    def start_discussion(self):
        """Start the focus group discussion"""
        self.status = 'active'
        self.current_round = 1
        
        # Create first round
        first_round = FocusGroupRound(
            focus_group_id=self.id,
            round_number=1,
            prompt=self.initial_question,
            status='active'
        )
        db.session.add(first_round)
        db.session.commit()
        return first_round
    
    def next_round(self, prompt=None):
        """Move to the next round"""
        if self.current_round >= self.max_rounds:
            self.status = 'completed'
            db.session.commit()
            return None
        
        # Complete current round
        current = self.rounds.filter_by(round_number=self.current_round).first()
        if current:
            current.status = 'completed'
        
        # Create next round
        self.current_round += 1
        next_round = FocusGroupRound(
            focus_group_id=self.id,
            round_number=self.current_round,
            prompt=prompt or f"Round {self.current_round} discussion",
            status='active'
        )
        db.session.add(next_round)
        db.session.commit()
        return next_round
    
    def get_current_round(self):
        """Get the current active round"""
        return self.rounds.filter_by(round_number=self.current_round).first()
    
    def get_sentiment_evolution(self):
        """Get sentiment evolution across rounds"""
        evolution = []
        for round_obj in self.rounds.order_by(FocusGroupRound.round_number):
            round_data = {
                'round': round_obj.round_number,
                'participants': {}
            }
            for message in round_obj.messages:
                participant_id = message.participant_id
                if participant_id not in round_data['participants']:
                    round_data['participants'][participant_id] = []
                round_data['participants'][participant_id].append({
                    'sentiment': message.sentiment_score,
                    'timestamp': message.created_at.isoformat()
                })
            evolution.append(round_data)
        return evolution

class FocusGroupParticipant(BaseModel):
    """Participant in a focus group"""
    __tablename__ = 'focus_group_participants'
    
    focus_group_id = db.Column(db.String(36), db.ForeignKey('focus_groups.id'), nullable=False)
    persona_id = db.Column(db.String(36), db.ForeignKey('personas.id'), nullable=False)
    role = db.Column(db.String(20), default='participant')  # participant, moderator
    
    # Participation metadata
    is_active = db.Column(db.Boolean, default=True)
    influence_score = db.Column(db.Float, default=0.0)  # Calculated influence on group
    
    # Relationships
    persona = db.relationship('Persona', backref='focus_group_participations')
    messages = db.relationship('RoundMessage', backref='participant', lazy='dynamic')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('focus_group_id', 'persona_id', name='_focus_group_persona_uc'),)
    
    def __repr__(self):
        return f'<FocusGroupParticipant {self.persona_id} in {self.focus_group_id}>'
    
    def to_dict(self):
        """Convert to dictionary with persona data"""
        result = super().to_dict()
        result['persona'] = self.persona.to_dict() if self.persona else None
        result['message_count'] = self.messages.count()
        return result
    
    def get_sentiment_trend(self):
        """Get sentiment trend for this participant"""
        messages = self.messages.order_by(RoundMessage.created_at.asc()).all()
        return [(msg.round_number, msg.sentiment_score, msg.created_at.isoformat()) 
                for msg in messages if msg.sentiment_score is not None]

class FocusGroupRound(BaseModel):
    """Individual round in a focus group discussion"""
    __tablename__ = 'focus_group_rounds'
    
    focus_group_id = db.Column(db.String(36), db.ForeignKey('focus_groups.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    
    # Round metadata
    status = db.Column(db.String(20), default='pending')  # pending, active, completed
    summary = db.Column(db.Text)  # AI-generated round summary
    key_themes = db.Column(JSON)  # Extracted themes
    
    # Relationships
    messages = db.relationship('RoundMessage', backref='round', lazy='dynamic', cascade='all, delete-orphan')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('focus_group_id', 'round_number', name='_focus_group_round_uc'),)
    
    def __repr__(self):
        return f'<FocusGroupRound {self.round_number} of {self.focus_group_id}>'
    
    def to_dict(self):
        """Convert to dictionary with messages"""
        result = super().to_dict()
        result['message_count'] = self.messages.count()
        result['messages'] = [msg.to_dict() for msg in self.messages.order_by(RoundMessage.created_at)]
        return result
    
    def add_message(self, participant_id, content, sentiment_score=None, metadata=None):
        """Add a message to this round"""
        message = RoundMessage(
            round_id=self.id,
            participant_id=participant_id,
            content=content,
            sentiment_score=sentiment_score,
            metadata=metadata or {}
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    def complete_round(self, summary=None, themes=None):
        """Mark round as completed"""
        self.status = 'completed'
        if summary:
            self.summary = summary
        if themes:
            self.key_themes = themes
        self.updated_at = datetime.utcnow()
        db.session.commit()

class RoundMessage(BaseModel):
    """Message in a focus group round"""
    __tablename__ = 'round_messages'
    
    round_id = db.Column(db.String(36), db.ForeignKey('focus_group_rounds.id'), nullable=False)
    participant_id = db.Column(db.String(36), db.ForeignKey('focus_group_participants.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Message analysis
    sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    influence_score = db.Column(db.Float)  # Impact on other participants
    message_metadata = db.Column(JSON)  # Additional message data
    
    # Processing metadata
    processing_time = db.Column(db.Float)
    token_count = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<RoundMessage {self.id[:8]}... in round {self.round_id}>'
    
    def to_dict(self):
        """Convert to dictionary with participant info"""
        result = super().to_dict()
        if self.participant:
            result['participant_name'] = self.participant.persona.name if self.participant.persona else 'Unknown'
            result['participant_avatar'] = self.participant.persona.avatar if self.participant.persona else '👤'
        return result 