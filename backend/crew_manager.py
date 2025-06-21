import os
import yaml
from typing import Dict, List, Any, Optional
from crewai import Agent, Crew, Task, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import uuid

class CrewManager:
    """Manages CrewAI agents and tasks for MeshAI backend"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=gemini_api_key,
            temperature=0.7
        )
        
        # Load configurations
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')
        
        # Cache for created agents
        self._agent_cache = {}
    
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
    
    def create_agent(self, agent_name: str) -> Optional[Agent]:
        """Create or retrieve cached agent"""
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        if agent_name not in self.agents_config:
            print(f"Agent configuration for '{agent_name}' not found")
            return None
        
        config = self.agents_config[agent_name]
        
        # Use the centralized LLM instance instead of config LLM
        agent = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,  # Always use the same Gemini LLM instance
            verbose=False,
            allow_delegation=False,
            memory=True
        )
        
        self._agent_cache[agent_name] = agent
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
                sentiment, score = self._analyze_sentiment(response_text)
                
                # Get persona info from agents config
                persona_config = self.agents_config[agent_name]
                
                reactions.append({
                    "persona_id": persona_id,
                    "name": persona_config['role'],
                    "avatar": self._get_avatar_for_persona(persona_id),
                    "reaction": response_text,
                    "sentiment": sentiment,
                    "sentiment_score": score
                })
                
            except Exception as e:
                print(f"Error with persona {persona_id}: {e}")
                # Fallback response
                persona_config = self.agents_config.get(agent_name, {})
                reactions.append({
                    "persona_id": persona_id,
                    "name": persona_config.get('role', 'Unknown Role'),
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
                sentiment, score = self._analyze_sentiment(response_text)
                
                persona_config = self.agents_config[agent_name]
                
                discussion_messages.append({
                    "id": str(uuid.uuid4()),
                    "persona_id": persona_id,
                    "persona_name": persona_config['role'],
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
            agent_name = persona_id.replace('-', '_')
            agent = self.create_agent(agent_name)
            
            if not agent:
                continue
            
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
                sentiment, score = self._analyze_sentiment(response_text)
                
                persona_config = self.agents_config[agent_name]
                
                initial_reactions.append({
                    "persona_id": persona_id,
                    "persona_name": persona_config['role'],
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
                    sentiment, score = self._analyze_sentiment(response_text)
                    
                    persona_config = self.agents_config[agent_name]
                    
                    message = {
                        "id": str(uuid.uuid4()),
                        "persona_id": persona_id,
                        "persona_name": persona_config['role'],
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
                agent_name=agents_data[0][2]
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
        """Get avatar emoji for persona"""
        avatar_map = {
            "tech-enthusiast": "🤖",
            "price-sensitive": "💰",
            "eco-conscious": "🌱",
            "early-adopter": "🚀",
            "skeptical-buyer": "🤔",
            "marketing-manager": "👩‍💼",
            "software-engineer": "👨‍💻",
            "product-manager": "👩‍🔬",
            "sales-executive": "👨‍💼",
            "data-analyst": "👩‍🎓"
        }
        return avatar_map.get(persona_id, "👤")
    
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