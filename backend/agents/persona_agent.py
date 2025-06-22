from typing import Dict, Any, List, Optional
import json
import re
import time
from .base import BaseAgent
from models.persona import Persona
from core.logging import agent_logger
from core.exceptions import PersonaError

class PersonaAgent(BaseAgent):
    """Agent representing a specific persona with defined traits and behaviors"""
    
    def __init__(self, 
                 persona: Persona,
                 llm_config: Dict[str, Any] = None,
                 verbose: bool = True):
        
        self.persona = persona
        self.persona_id = persona.id
        
        # Build persona-specific prompt components
        role = f"Persona: {persona.name}"
        goal = self._build_goal()
        backstory = self._build_backstory()
        
        super().__init__(
            name=persona.name,
            role=role,
            goal=goal,
            backstory=backstory,
            llm_config=llm_config,
            verbose=verbose
        )
        
        # Persona-specific context
        self.update_context('persona_traits', persona.personality_traits or {})
        self.update_context('sentiment_bias', persona.sentiment_bias)
        self.update_context('engagement_level', persona.engagement_level)
        self.update_context('controversy_tolerance', persona.controversy_tolerance)
        
        agent_logger.info(f"PersonaAgent created for {persona.name}", 
                         persona_id=persona.id, agent_id=self.id)
    
    def _build_goal(self) -> str:
        """Build the goal statement for this persona"""
        base_goal = f"Respond authentically as {self.persona.name}, maintaining consistency with your personality traits and background."
        
        if self.persona.expertise_areas:
            expertise = ", ".join(self.persona.expertise_areas)
            base_goal += f" Draw from your expertise in: {expertise}."
        
        return base_goal
    
    def _build_backstory(self) -> str:
        """Build the backstory for this persona"""
        backstory_parts = [
            f"You are {self.persona.name}.",
            f"Description: {self.persona.description}"
        ]
        
        if self.persona.background_context:
            backstory_parts.append(f"Background: {self.persona.background_context}")
        
        if self.persona.communication_style:
            backstory_parts.append(f"Communication Style: {self.persona.communication_style}")
        
        # Add personality traits
        if self.persona.personality_traits:
            traits_text = self._format_personality_traits()
            backstory_parts.append(f"Personality Traits: {traits_text}")
        
        # Add behavioral parameters
        behavioral_context = self._build_behavioral_context()
        if behavioral_context:
            backstory_parts.append(behavioral_context)
        
        return " ".join(backstory_parts)
    
    def _format_personality_traits(self) -> str:
        """Format personality traits into readable text"""
        if not self.persona.personality_traits:
            return ""
        
        traits = []
        for trait, value in self.persona.personality_traits.items():
            if isinstance(value, (int, float)):
                if value > 0.7:
                    traits.append(f"very {trait}")
                elif value > 0.4:
                    traits.append(f"moderately {trait}")
                elif value < 0.3:
                    traits.append(f"not very {trait}")
            else:
                traits.append(f"{trait}: {value}")
        
        return ", ".join(traits)
    
    def _build_behavioral_context(self) -> str:
        """Build behavioral context from persona parameters"""
        context_parts = []
        
        # Sentiment bias
        if self.persona.sentiment_bias > 0.3:
            context_parts.append("You tend to be optimistic and positive in your responses.")
        elif self.persona.sentiment_bias < -0.3:
            context_parts.append("You tend to be more critical and skeptical in your responses.")
        
        # Engagement level
        if self.persona.engagement_level > 0.7:
            context_parts.append("You are highly engaged and enthusiastic in discussions.")
        elif self.persona.engagement_level < 0.3:
            context_parts.append("You are more reserved and measured in your participation.")
        
        # Controversy tolerance
        if self.persona.controversy_tolerance > 0.7:
            context_parts.append("You're comfortable with controversial topics and debates.")
        elif self.persona.controversy_tolerance < 0.3:
            context_parts.append("You prefer to avoid controversial topics when possible.")
        
        return " ".join(context_parts)
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a message and generate a persona-appropriate response"""
        try:
            start_time = time.time()
            
            # Build the full prompt with persona context
            prompt = self._build_prompt(message, context)
            
            # Get response from the LLM directly
            response = self.llm.invoke(prompt).content
            
            # Process and analyze the response
            processed_response = self._process_response(response)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            
            # Add to memory
            self.add_to_memory(message, processed_response['content'], {
                'processing_time': processing_time,
                'sentiment_score': processed_response['sentiment_score'],
                'context': context
            })
            
            agent_logger.info(f"Processed message for {self.name}", 
                            agent_id=self.id, processing_time=processing_time)
            
            return {
                'content': processed_response['content'],
                'sentiment_score': processed_response['sentiment_score'],
                'processing_time': processing_time,
                'persona_id': self.persona_id,
                'persona_name': self.persona.name,
                'persona_avatar': self.persona.avatar,
                'metadata': processed_response.get('metadata', {})
            }
            
        except Exception as e:
            agent_logger.error(f"Error processing message for {self.name}", 
                             agent_id=self.id, error=str(e))
            raise PersonaError(f"Failed to process message: {str(e)}", 
                             persona_id=self.persona_id)
    
    def _build_prompt(self, message: str, context: Dict[str, Any] = None) -> str:
        """Build the complete prompt for the LLM"""
        prompt_parts = []
        
        # Add conversation history for context
        memory_context = self.get_memory_context(limit=5)
        if memory_context:
            prompt_parts.append(f"Previous conversation:\n{memory_context}\n")
        
        # Add additional context if provided
        if context:
            if 'focus_group_context' in context:
                prompt_parts.append(f"Focus group context: {context['focus_group_context']}\n")
            if 'other_responses' in context:
                prompt_parts.append(f"Other participants have said: {context['other_responses']}\n")
        
        # Add the main message
        prompt_parts.append(f"Please respond to: {message}")
        
        # Add persona-specific instructions
        prompt_parts.append(self._get_response_instructions())
        
        return "\n".join(prompt_parts)
    
    def _get_response_instructions(self) -> str:
        """Get persona-specific response instructions"""
        instructions = [
            f"Respond as {self.persona.name}.",
            "Stay true to your personality traits and background.",
            "Keep your response natural and conversational."
        ]
        
        # Add length guidance based on engagement level
        if self.persona.engagement_level > 0.7:
            instructions.append("Feel free to elaborate and share detailed thoughts.")
        elif self.persona.engagement_level < 0.3:
            instructions.append("Keep your response concise and to the point.")
        
        return " ".join(instructions)
    
    def _process_response(self, raw_response: str) -> Dict[str, Any]:
        """Process the raw LLM response"""
        # Clean up the response
        content = raw_response.strip()
        
        # Calculate sentiment score based on persona bias and content
        sentiment_score = self._calculate_sentiment(content)
        
        # Extract any metadata
        metadata = self._extract_metadata(content)
        
        return {
            'content': content,
            'sentiment_score': sentiment_score,
            'metadata': metadata
        }
    
    def _calculate_sentiment(self, content: str) -> float:
        """Calculate sentiment score for the response"""
        # Simple sentiment analysis based on keywords and persona bias
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'enjoy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'wrong', 'problem', 'issue']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Base sentiment from content
        if positive_count > negative_count:
            base_sentiment = 0.3 + (positive_count - negative_count) * 0.1
        elif negative_count > positive_count:
            base_sentiment = -0.3 - (negative_count - positive_count) * 0.1
        else:
            base_sentiment = 0.0
        
        # Apply persona bias
        final_sentiment = base_sentiment + (self.persona.sentiment_bias * 0.5)
        
        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, final_sentiment))
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from the response"""
        metadata = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'has_questions': '?' in content,
            'has_exclamations': '!' in content
        }
        
        return metadata
    
    def get_persona_summary(self) -> Dict[str, Any]:
        """Get a summary of this persona agent"""
        return {
            'persona_id': self.persona_id,
            'name': self.persona.name,
            'description': self.persona.description,
            'avatar': self.persona.avatar,
            'traits': self.persona.personality_traits,
            'sentiment_bias': self.persona.sentiment_bias,
            'engagement_level': self.persona.engagement_level,
            'controversy_tolerance': self.persona.controversy_tolerance,
            'conversation_count': len(self.conversation_history),
            'agent_id': self.id
        } 