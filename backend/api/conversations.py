from flask import Blueprint, request, jsonify
import traceback
from datetime import datetime
import uuid

from core.logging import api_logger
from core.exceptions import MeshAIException
from services.persona_service import PersonaService
from agents.persona_agent import PersonaAgent

# Use the existing api logger
conversations_logger = api_logger

conversations_bp = Blueprint('conversations', __name__)

@conversations_bp.route('/simple-interaction', methods=['POST'])
def simple_interaction():
    """Generate simple reactions from selected personas to a question"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        question = data.get('question', '').strip()
        persona_ids = data.get('personas', [])
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        if not persona_ids:
            return jsonify({
                'success': False,
                'error': 'At least one persona is required'
            }), 400
        
        # Get personas from database
        persona_service = PersonaService()
        personas = persona_service.get_personas_by_ids(persona_ids)
        
        if not personas:
            return jsonify({
                'success': False,
                'error': 'No valid personas found'
            }), 400
        
        # Generate reactions using PersonaAgent
        reactions = []
        for persona in personas:
            try:
                agent = PersonaAgent(persona)
                response_data = agent.process_message(question)
                response = response_data.get('content', '')
                
                # Determine sentiment from response
                sentiment = "neutral"
                sentiment_score = 0
                
                if response:
                    # Simple sentiment analysis based on persona's sentiment_bias
                    if persona.sentiment_bias > 0.2:
                        sentiment = "positive"
                        sentiment_score = 1
                    elif persona.sentiment_bias < -0.2:
                        sentiment = "negative" 
                        sentiment_score = -1
                
                reactions.append({
                    'persona_id': persona.id,
                    'name': persona.name,
                    'avatar': persona.avatar,
                    'reaction': response,
                    'sentiment': sentiment,
                    'sentiment_score': sentiment_score
                })
                
            except Exception as e:
                conversations_logger.error(f"Error generating reaction for persona {persona.id}: {str(e)}")
                # Add fallback reaction
                reactions.append({
                    'persona_id': persona.id,
                    'name': persona.name,
                    'avatar': persona.avatar,
                    'reaction': f"I'd like to think more about this question: {question}",
                    'sentiment': "neutral",
                    'sentiment_score': 0
                })
        
        conversations_logger.info(f"Generated {len(reactions)} reactions for question", 
                                question=question[:50], persona_count=len(personas))
        
        return jsonify({
            'success': True,
            'data': {
                'question': question,
                'reactions': reactions,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        conversations_logger.error(f"Error in simple interaction: {str(e)}", 
                                 error=str(e), traceback=traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to generate reactions',
            'message': str(e)
        }), 500

@conversations_bp.route('/group-discussion', methods=['POST'])
def group_discussion():
    """Generate a group discussion between personas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        question = data.get('question', '').strip()
        persona_ids = data.get('personas', [])
        initial_reactions = data.get('initial_reactions', [])
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        if not persona_ids:
            return jsonify({
                'success': False,
                'error': 'At least one persona is required'
            }), 400
        
        # Get personas from database
        persona_service = PersonaService()
        personas = persona_service.get_personas_by_ids(persona_ids)
        
        if not personas:
            return jsonify({
                'success': False,
                'error': 'No valid personas found'
            }), 400
        
        # Generate discussion messages
        discussion_messages = []
        
        # Create agents for each persona
        agents = {}
        for persona in personas:
            agents[persona.id] = PersonaAgent(persona)
        
        # Simulate 2-3 rounds of discussion
        for round_num in range(2):
            for persona in personas:
                try:
                    agent = agents[persona.id]
                    
                    # Build context from previous messages
                    context = f"Question: {question}\n\n"
                    if discussion_messages:
                        context += "Previous discussion:\n"
                        for msg in discussion_messages[-3:]:  # Last 3 messages for context
                            context += f"{msg['persona_name']}: {msg['content']}\n"
                    
                    response_data = agent.process_message(context)
                    response = response_data.get('content', '')
                    
                    # Determine sentiment
                    sentiment = "neutral"
                    sentiment_score = 0
                    
                    if response:
                        if persona.sentiment_bias > 0.2:
                            sentiment = "positive"
                            sentiment_score = 1
                        elif persona.sentiment_bias < -0.2:
                            sentiment = "negative"
                            sentiment_score = -1
                    
                    discussion_messages.append({
                        'id': str(uuid.uuid4()),
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'avatar': persona.avatar,
                        'content': response,
                        'sentiment': sentiment,
                        'sentiment_score': sentiment_score,
                        'timestamp': datetime.now().isoformat(),
                        'round': round_num + 1
                    })
                    
                except Exception as e:
                    conversations_logger.error(f"Error generating discussion message for persona {persona.id}: {str(e)}")
                    # Add fallback message
                    discussion_messages.append({
                        'id': str(uuid.uuid4()),
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'avatar': persona.avatar,
                        'content': f"I need more time to consider this aspect of the question.",
                        'sentiment': "neutral",
                        'sentiment_score': 0,
                        'timestamp': datetime.now().isoformat(),
                        'round': round_num + 1
                    })
        
        conversations_logger.info(f"Generated {len(discussion_messages)} discussion messages", 
                                question=question[:50], persona_count=len(personas))
        
        return jsonify({
            'success': True,
            'data': {
                'question': question,
                'discussion_messages': discussion_messages,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        conversations_logger.error(f"Error in group discussion: {str(e)}", 
                                 error=str(e), traceback=traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to generate group discussion',
            'message': str(e)
        }), 500

@conversations_bp.route('/focus-group', methods=['POST'])
def focus_group_simulation():
    """Generate a comprehensive focus group simulation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        campaign_description = data.get('campaign_description', '').strip()
        persona_ids = data.get('personas', [])
        goals = data.get('goals', [])
        
        if not campaign_description:
            return jsonify({
                'success': False,
                'error': 'Campaign description is required'
            }), 400
        
        if not persona_ids:
            return jsonify({
                'success': False,
                'error': 'At least one persona is required'
            }), 400
        
        # Get personas from database
        persona_service = PersonaService()
        personas = persona_service.get_personas_by_ids(persona_ids)
        
        if not personas:
            return jsonify({
                'success': False,
                'error': 'No valid personas found'
            }), 400
        
        session_id = str(uuid.uuid4())
        
        # Generate initial reactions
        initial_reactions = []
        discussion_messages = []
        sentiment_intervals = []
        
        # Create agents for each persona
        agents = {}
        for persona in personas:
            agents[persona.id] = PersonaAgent(persona)
        
        # Phase 1: Initial reactions
        for persona in personas:
            try:
                agent = agents[persona.id]
                prompt = f"Campaign: {campaign_description}\n\nGoals: {', '.join(goals) if goals else 'General feedback'}\n\nWhat is your initial reaction to this campaign?"
                
                response_data = agent.process_message(prompt)
                response = response_data.get('content', '')
                
                sentiment = "neutral"
                sentiment_score = 0
                
                if response:
                    if persona.sentiment_bias > 0.2:
                        sentiment = "positive"
                        sentiment_score = 1
                    elif persona.sentiment_bias < -0.2:
                        sentiment = "negative"
                        sentiment_score = -1
                
                initial_reactions.append({
                    'persona_id': persona.id,
                    'name': persona.name,
                    'avatar': persona.avatar,
                    'reaction': response,
                    'sentiment': sentiment,
                    'sentiment_score': sentiment_score
                })
                
            except Exception as e:
                conversations_logger.error(f"Error generating initial reaction for persona {persona.id}: {str(e)}")
                initial_reactions.append({
                    'persona_id': persona.id,
                    'name': persona.name,
                    'avatar': persona.avatar,
                    'reaction': f"I'd like to learn more about this campaign before sharing my thoughts.",
                    'sentiment': "neutral",
                    'sentiment_score': 0
                })
        
        # Phase 2: Discussion rounds
        for round_num in range(3):  # 3 rounds of discussion
            round_messages = []
            persona_sentiments = {}
            
            for persona in personas:
                try:
                    agent = agents[persona.id]
                    
                    # Build context
                    context = f"Campaign: {campaign_description}\n\n"
                    if goals:
                        context += f"Goals: {', '.join(goals)}\n\n"
                    
                    if discussion_messages:
                        context += "Previous discussion:\n"
                        for msg in discussion_messages[-6:]:  # Last 6 messages for context
                            context += f"{msg['persona_name']}: {msg['content']}\n"
                    
                    context += f"\nRound {round_num + 1}: Please share your thoughts and respond to others' comments."
                    
                    response_data = agent.process_message(context)
                    response = response_data.get('content', '')
                    
                    sentiment = "neutral"
                    sentiment_score = 0
                    
                    if response:
                        if persona.sentiment_bias > 0.2:
                            sentiment = "positive"
                            sentiment_score = 1
                        elif persona.sentiment_bias < -0.2:
                            sentiment = "negative"
                            sentiment_score = -1
                    
                    message = {
                        'id': str(uuid.uuid4()),
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'avatar': persona.avatar,
                        'content': response,
                        'sentiment': sentiment,
                        'sentiment_score': sentiment_score,
                        'timestamp': datetime.now().isoformat(),
                        'round': round_num + 1
                    }
                    
                    round_messages.append(message)
                    persona_sentiments[persona.id] = sentiment_score
                    
                except Exception as e:
                    conversations_logger.error(f"Error generating round {round_num + 1} message for persona {persona.id}: {str(e)}")
                    message = {
                        'id': str(uuid.uuid4()),
                        'persona_id': persona.id,
                        'persona_name': persona.name,
                        'avatar': persona.avatar,
                        'content': f"I'm still processing the information from this round.",
                        'sentiment': "neutral",
                        'sentiment_score': 0,
                        'timestamp': datetime.now().isoformat(),
                        'round': round_num + 1
                    }
                    round_messages.append(message)
                    persona_sentiments[persona.id] = 0
            
            discussion_messages.extend(round_messages)
            
            # Calculate overall sentiment for this round
            overall_sentiment = sum(persona_sentiments.values()) / len(persona_sentiments) if persona_sentiments else 0
            
            sentiment_intervals.append({
                'round': round_num + 1,
                'timestamp': datetime.now().isoformat(),
                'overall_sentiment': overall_sentiment,
                'persona_sentiments': persona_sentiments
            })
        
        # Generate final summary
        all_sentiments = [reaction['sentiment_score'] for reaction in initial_reactions]
        all_sentiments.extend([msg['sentiment_score'] for msg in discussion_messages])
        
        overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
        
        # Calculate sentiment shift (final vs initial)
        initial_sentiment = sum([r['sentiment_score'] for r in initial_reactions]) / len(initial_reactions) if initial_reactions else 0
        final_sentiment = sentiment_intervals[-1]['overall_sentiment'] if sentiment_intervals else 0
        sentiment_shift = final_sentiment - initial_sentiment
        
        # Generate key insights (simplified)
        key_insights = [
            f"Overall sentiment: {'Positive' if overall_sentiment > 0.2 else 'Negative' if overall_sentiment < -0.2 else 'Neutral'}",
            f"Sentiment {'improved' if sentiment_shift > 0.1 else 'declined' if sentiment_shift < -0.1 else 'remained stable'} during discussion",
            f"Engaged {len(personas)} personas in {len(discussion_messages)} discussion points"
        ]
        
        recommendations = [
            "Consider the feedback from different persona perspectives",
            "Address concerns raised during the discussion",
            "Leverage positive aspects highlighted by personas"
        ]
        
        final_summary = {
            'overall_sentiment': overall_sentiment,
            'sentiment_shift': sentiment_shift,
            'key_insights': key_insights,
            'recommendations': recommendations
        }
        
        conversations_logger.info(f"Generated focus group simulation", 
                                session_id=session_id, persona_count=len(personas), 
                                message_count=len(discussion_messages))
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'campaign_description': campaign_description,
                'initial_reactions': initial_reactions,
                'discussion_messages': discussion_messages,
                'sentiment_intervals': sentiment_intervals,
                'final_summary': final_summary
            }
        })
        
    except Exception as e:
        conversations_logger.error(f"Error in focus group simulation: {str(e)}", 
                                 error=str(e), traceback=traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to generate focus group simulation',
            'message': str(e)
        }), 500

@conversations_bp.route('/custom-persona', methods=['POST'])
def create_custom_persona():
    """Create a custom persona (frontend compatibility endpoint)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Transform frontend data to backend format
        persona_data = {
            'name': data.get('name', '').strip(),
            'description': data.get('description', '').strip(),
            'avatar': data.get('avatar', '👤'),
            'expertise_areas': data.get('traits', []),  # Frontend 'traits' -> backend 'expertise_areas'
            'communication_style': 'Friendly and helpful',
            'background_context': f"Custom persona: {data.get('description', '')}",
            'sentiment_bias': 0.0,
            'engagement_level': 0.7,
            'controversy_tolerance': 0.5
        }
        
        if not persona_data['name']:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        if not persona_data['description']:
            return jsonify({
                'success': False,
                'error': 'Description is required'
            }), 400
        
        # Create persona using service
        persona_service = PersonaService()
        persona = persona_service.create_persona(persona_data)
        
        conversations_logger.info(f"Created custom persona: {persona.name}", persona_id=persona.id)
        
        return jsonify({
            'success': True,
            'data': {
                'success': True,
                'persona': persona.to_frontend_dict(),
                'message': f'Custom persona "{persona.name}" created successfully'
            }
        })
        
    except Exception as e:
        conversations_logger.error(f"Error creating custom persona: {str(e)}", 
                                 error=str(e), traceback=traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to create custom persona',
            'message': str(e)
        }), 500 