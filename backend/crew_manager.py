import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Crew, Task, Process, LLM 
from datetime import datetime
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class CrewManager:
    """Manages CrewAI agents and tasks for MeshAI backend"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.7,
            max_tokens=2000  # Increased for longer, more complete responses
        )
        
        # Load configurations
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')
        
        # Cache for created agents
        self._agent_cache = {}

    def _load_personas_from_json(self) -> Dict:
        """Load personas from JSON files in the personas directory"""
        personas = {}
        personas_dir = os.path.join(os.path.dirname(__file__), "personas")
        
        if not os.path.exists(personas_dir):
            print(f"Personas directory not found: {personas_dir}")
            return personas
        
        for filename in os.listdir(personas_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(personas_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        persona_data = json.load(f)
                        # Use filename without extension as the key
                        persona_id = filename.replace('.json', '')
                        personas[persona_id] = {
                            'role': persona_data.get('name', 'Unknown'),
                            'goal': f"Provide insights as {persona_data.get('role', 'a participant')}",
                            'backstory': persona_data.get('description', 'A focus group participant'),
                            'avatar': persona_data.get('avatar', '👤')
                        }
                except Exception as e:
                    print(f"Error loading persona {filename}: {e}")
                    continue
        
        return personas
    
    def _load_config(self, filepath: str) -> Dict:
        """Load YAML configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), filepath)
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {filepath} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {filepath}: {e}")
            return {}
    
    def create_agent(self, persona_id: str) -> Optional[Agent]:
        """Create or retrieve cached agent from persona JSON files"""
        if persona_id in self._agent_cache:
            return self._agent_cache[persona_id]
        
        # Load personas from JSON if not already loaded
        if not hasattr(self, '_personas_from_json'):
            self._personas_from_json = self._load_personas_from_json()
        
        # Try both the original persona_id and the converted version
        lookup_id = persona_id
        if persona_id not in self._personas_from_json:
            # Try converting from underscore to hyphen format
            alt_id = persona_id.replace('_', '-')
            if alt_id in self._personas_from_json:
                lookup_id = alt_id
            else:
                # Try converting from hyphen to underscore format
                alt_id = persona_id.replace('-', '_')
                if alt_id in self._personas_from_json:
                    lookup_id = alt_id
                else:
                    print(f"Persona configuration for '{persona_id}' not found in JSON files")
                    print(f"Available personas: {list(self._personas_from_json.keys())}")
                    return None
        
        config = self._personas_from_json[lookup_id]
        
        # Create agent from persona data
        agent = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
            memory=True
        )
        
        self._agent_cache[persona_id] = agent
        return agent
    
    def create_task(self, task_type: str, agent: Agent, **kwargs) -> Optional[Task]:
        """Create a task with dynamic parameters"""
        if task_type not in self.tasks_config:
            print(f"Task configuration for '{task_type}' not found")
            return None
        
        task_config = self.tasks_config[task_type]
        
        # Format description and expected_output with provided kwargs
        description = task_config['description'].format(**kwargs)
        expected_output = task_config['expected_output'].format(**kwargs)
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent
        )
    
    def run_simple_interaction(self, question: str, selected_personas: List[str]) -> List[Dict]:
        """Handle simple Q&A interaction with selected personas"""
        reactions = []
        
        for persona_id in selected_personas:
            # Convert persona_id format (e.g., "tech-enthusiast" -> "tech_enthusiast")
            agent_name = persona_id.replace('-', '_')
            
            agent = self.create_agent(agent_name)
            if not agent:
                continue
            
            task = self.create_task(
                'initial_reaction_task',
                agent,
                topic=question,
                context="Simple Q&A interaction",
                agent_name=agent_name
            )
            
            if not task:
                continue
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                response_text = str(result)
                logger.info(f"CrewAI Response for {persona_id}: {response_text}")
                sentiment, score = self._analyze_sentiment(response_text)
                
                # Get persona info from JSON data instead of agents_config
                if hasattr(self, '_personas_from_json') and persona_id in self._personas_from_json:
                    persona_name = self._personas_from_json[persona_id]['role']
                else:
                    # Fallback to agents_config
                    persona_config = self.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                reactions.append({
                    "persona_id": persona_id,
                    "name": persona_name,
                    "avatar": self._get_avatar_for_persona(persona_id),
                    "reaction": response_text,
                    "sentiment": sentiment,
                    "sentiment_score": score
                })
                
            except Exception as e:
                print(f"Error with persona {persona_id}: {e}")
                # Fallback response
                if hasattr(self, '_personas_from_json') and persona_id in self._personas_from_json:
                    persona_name = self._personas_from_json[persona_id]['role']
                else:
                    persona_config = self.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                reactions.append({
                    "persona_id": persona_id,
                    "name": persona_name,
                    "avatar": self._get_avatar_for_persona(persona_id),
                    "reaction": f"{e}",
                    "sentiment": "neutral",
                    "sentiment_score": 0
                })
        
        return reactions
    
    def run_group_discussion(self, question: str, selected_personas: List[str], initial_reactions: List[Dict]) -> List[Dict]:
        """Handle group discussion between personas"""
        discussion_messages = []
        
        for persona_id in selected_personas:
            agent_name = persona_id.replace('-', '_')
            agent = self.create_agent(agent_name)
            
            if not agent:
                continue
            
            # Create context from other reactions
            other_reactions = [r for r in initial_reactions if r["persona_id"] != persona_id]
            other_reactions_text = "\n".join([f"{r['name']}: {r['reaction']}" for r in other_reactions])
            
            task = self.create_task(
                'group_discussion_task',
                agent,
                topic=question,
                other_reactions=other_reactions_text,
                round_number=1,
                agent_name=agent_name
            )
            
            if not task:
                continue
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                response_text = str(result)
                logger.info(f"CrewAI Group Discussion Response for {persona_id}: {response_text}")
                sentiment, score = self._analyze_sentiment(response_text)
                
                # Get persona info from JSON data instead of agents_config
                if hasattr(self, '_personas_from_json') and persona_id in self._personas_from_json:
                    persona_name = self._personas_from_json[persona_id]['role']
                else:
                    # Fallback to agents_config
                    persona_config = self.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                discussion_messages.append({
                    "id": str(uuid.uuid4()),
                    "persona_id": persona_id,
                    "persona_name": persona_name,
                    "avatar": self._get_avatar_for_persona(persona_id),
                    "content": response_text,
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "timestamp": datetime.now().isoformat(),
                    "round": 1
                })
                
            except Exception as e:
                print(f"Error in discussion with persona {persona_id}: {e}")
        
        return discussion_messages
    
    def run_focus_group_simulation(self, campaign_description: str, selected_personas: List[str], session_goals: List[str]) -> Dict:
        """Handle comprehensive focus group simulation"""
        
        # Phase 1: Initial Reactions
        initial_reactions = []
        agents_data = []
        
        for persona_id in selected_personas:
            agent = self.create_agent(persona_id)
            
            if not agent:
                continue
            
            # Convert persona_id to agent_name format for config lookup
            agent_name = persona_id.replace('-', '_')
            agents_data.append((persona_id, agent, agent_name))
            
            task = self.create_task(
                'focus_group_initial_task',
                agent,
                campaign_description=campaign_description,
                session_goals=", ".join(session_goals),
                agent_name=agent_name
            )
            
            if not task:
                continue
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            try:
                result = crew.kickoff()
                response_text = str(result)
                logger.info(f"CrewAI Focus Group Initial Reaction for {persona_id}: {response_text}")
                sentiment, score = self._analyze_sentiment(response_text)
                
                # Get persona info from JSON data instead of agents_config
                if hasattr(self, '_personas_from_json') and persona_id in self._personas_from_json:
                    persona_name = self._personas_from_json[persona_id]['role']
                else:
                    # Fallback to agents_config
                    persona_config = self.agents_config.get(agent_name, {})
                    persona_name = persona_config.get('role', 'Unknown Role')
                
                initial_reactions.append({
                    "persona_id": persona_id,
                    "persona_name": persona_name,
                    "avatar": self._get_avatar_for_persona(persona_id),
                    "reaction": response_text,
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "nps_score": max(0, min(10, 5 + score)),
                    "csat_score": max(1, min(5, 3 + score/2))
                })
                
            except Exception as e:
                print(f"Error in initial reaction for {persona_id}: {e}")
        
        # Phase 2: Group Discussion (3 rounds)
        discussion_messages = []
        sentiment_intervals = []
        
        for round_num in range(1, 4):
            round_messages = []
            
            for persona_id, agent, agent_name in agents_data:
                # Create context from previous discussion
                recent_messages = [m for m in discussion_messages[-6:] if m["persona_id"] != persona_id]
                recent_context = "\n".join([f"{m['persona_name']}: {m['content']}" for m in recent_messages])
                
                task = self.create_task(
                    'focus_group_discussion_task',
                    agent,
                    campaign_description=campaign_description,
                    recent_context=recent_context or "This is the start of the discussion.",
                    round_number=round_num,
                    agent_name=agent_name
                )
                
                if not task:
                    continue
                
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=False
                )
                
                try:
                    result = crew.kickoff()
                    response_text = str(result)
                    logger.info(f"CrewAI Focus Group Round {round_num} Response for {persona_id}: {response_text}")
                    sentiment, score = self._analyze_sentiment(response_text)
                    
                    # Get persona info from JSON data instead of agents_config
                    if hasattr(self, '_personas_from_json') and persona_id in self._personas_from_json:
                        persona_name = self._personas_from_json[persona_id]['role']
                    else:
                        # Fallback to agents_config
                        persona_config = self.agents_config.get(agent_name, {})
                        persona_name = persona_config.get('role', 'Unknown Role')
                    
                    message = {
                        "id": str(uuid.uuid4()),
                        "persona_id": persona_id,
                        "persona_name": persona_name,
                        "avatar": self._get_avatar_for_persona(persona_id),
                        "content": response_text,
                        "sentiment": sentiment,
                        "sentiment_score": score,
                        "timestamp": datetime.now().isoformat(),
                        "round": round_num
                    }
                    
                    round_messages.append(message)
                    discussion_messages.append(message)
                    
                except Exception as e:
                    print(f"Error in round {round_num} for {persona_id}: {e}")
            
            # Track sentiment at intervals
            if round_num in [2, 3]:
                round_sentiment = sum([m["sentiment_score"] for m in round_messages]) / len(round_messages) if round_messages else 0
                sentiment_intervals.append({
                    "round": round_num,
                    "average_sentiment": round_sentiment,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Phase 3: Final Summary
        if agents_data:
            summary_agent = agents_data[0][1]  # Use first agent as summarizer
            summary_agent_name = agents_data[0][2]  # Get the agent_name for the summary task
            
            # Create full context
            full_context = f"Initial Reactions:\n"
            for reaction in initial_reactions:
                full_context += f"{reaction['persona_name']}: {reaction['reaction']}\n"
            
            full_context += f"\nDiscussion Messages:\n"
            for msg in discussion_messages:
                full_context += f"Round {msg['round']} - {msg['persona_name']}: {msg['content']}\n"
            
            summary_task = self.create_task(
                'summary_synthesis_task',
                summary_agent,
                topic=campaign_description,
                full_discussion_context=full_context,
                agent_name=summary_agent_name
            )
            
            if summary_task:
                summary_crew = Crew(
                    agents=[summary_agent],
                    tasks=[summary_task],
                    process=Process.sequential,
                    verbose=False
                )
                
                try:
                    summary_result = summary_crew.kickoff()
                    final_summary = str(summary_result)
                    logger.info(f"CrewAI Focus Group Summary: {final_summary}")
                except Exception as e:
                    print(f"Error creating summary: {e}")
                    final_summary = "Summary generation encountered an error."
            else:
                final_summary = "Unable to generate summary due to task creation error."
        else:
            final_summary = "No agents available for summary generation."
        
        # Calculate overall metrics
        overall_sentiment = sum([r["sentiment_score"] for r in initial_reactions]) / len(initial_reactions) if initial_reactions else 0
        overall_nps = sum([r["nps_score"] for r in initial_reactions]) / len(initial_reactions) if initial_reactions else 5
        overall_csat = sum([r["csat_score"] for r in initial_reactions]) / len(initial_reactions) if initial_reactions else 3
        
        return {
            "campaign_description": campaign_description,
            "session_goals": session_goals,
            "initial_reactions": initial_reactions,
            "discussion_messages": discussion_messages,
            "sentiment_intervals": sentiment_intervals,
            "final_summary": final_summary,
            "overall_metrics": {
                "nps": round(overall_nps, 1),
                "csat": round(overall_csat, 1),
                "avg_sentiment": round(overall_sentiment, 1)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_sentiment(self, text: str) -> tuple[str, int]:
        """Analyze sentiment of text and return sentiment label and score"""
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'brilliant', 'outstanding', 'perfect', 'impressive', 'innovative', 'exciting', 'valuable', 'effective', 'successful']
        negative_words = ['terrible', 'awful', 'horrible', 'hate', 'disgusting', 'worst', 'disappointing', 'useless', 'failed', 'broken', 'concerning', 'problematic', 'challenging', 'difficult', 'expensive']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(5, positive_count - negative_count)
        elif negative_count > positive_count:
            sentiment = "negative" 
            score = max(-5, -(negative_count - positive_count))
        else:
            sentiment = "neutral"
            score = 0
            
        return sentiment, score
    
    def _get_avatar_for_persona(self, persona_id: str) -> str:
        """Get avatar emoji for persona from JSON data"""
        if not hasattr(self, '_personas_from_json'):
            self._personas_from_json = self._load_personas_from_json()
        
        # Try both the original persona_id and the converted version
        lookup_id = persona_id
        if persona_id not in self._personas_from_json:
            # Try converting from underscore to hyphen format
            alt_id = persona_id.replace('_', '-')
            if alt_id in self._personas_from_json:
                lookup_id = alt_id
            else:
                # Try converting from hyphen to underscore format
                alt_id = persona_id.replace('-', '_')
                if alt_id in self._personas_from_json:
                    lookup_id = alt_id
                else:
                    # Fallback to default avatar
                    return "👤"
        
        return self._personas_from_json[lookup_id]['avatar']
    
    def get_available_personas(self) -> List[Dict]:
        """Get list of available personas"""
        personas = []
        for agent_name, config in self.agents_config.items():
            persona_id = agent_name.replace('_', '-')
            personas.append({
                "id": persona_id,
                "name": config['role'],
                "description": config['backstory'][:100] + "...",
                "avatar": self._get_avatar_for_persona(persona_id)
            })
        return personas
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        return datetime.now().isoformat()
    
    def _generate_uuid(self) -> str:
        """Generate a UUID string"""
        return str(uuid.uuid4()) 