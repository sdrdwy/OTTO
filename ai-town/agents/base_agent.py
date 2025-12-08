"""
Base Agent Class
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
import json
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from utils.mock_llm import MockChatOpenAI
from utils.qwen_llm import QwenChatModel
from .persona_manager import persona_manager


class BaseAgent(ABC):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator, config_file: str = None, agent_type: str = "student"):
        self.memory = memory
        self.world = world
        # Initialize location to a valid location from the world map
        self.location = list(world.locations.keys())[0]  # Use the first available location
        
        # Initialize knowledge manager based on agent type
        from memory.knowledge_base import AgentKnowledgeManager
        self.knowledge_manager = AgentKnowledgeManager(agent_type)
        
        # Load agent configuration from file
        self.config_file = config_file
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.name = self.config.get("name", name)
            self.role = self.config.get("role", "Agent")
            self.personality_traits = self.config.get("personality_traits", [])
            self.communication_style = self.config.get("communication_style", "neutral")
            self.behavioral_patterns = self.config.get("behavioral_patterns", [])
            self.is_expert = self.config.get("is_expert", False)
            self.expertise = self.config.get("expertise", [])
            self.schedule_preferences = self.config.get("schedule_preferences", {})
            self.作息习惯 = self.config.get("作息习惯", {})
            self.learning_goals = self.config.get("learning_goals", [])
            self.preferred_locations = self.config.get("preferred_locations", [])
            self.social_preferences = self.config.get("social_preferences", [])
            self.activity_preferences = self.config.get("activity_preferences", [])
            self.teaching_style = self.config.get("teaching_style", [])
        else:
            # Default values if no config is provided
            self.config = {}
            self.name = name
            self.role = "Agent"
            self.personality_traits = []
            self.communication_style = "neutral"
            self.behavioral_patterns = []
            self.is_expert = False
            self.expertise = []
            self.schedule_preferences = {}
            self.作息习惯 = {}
            self.learning_goals = []
            self.preferred_locations = []
            self.social_preferences = []
            self.activity_preferences = []
            self.teaching_style = []
        
        # Check if we have DASHSCOPE API key for Qwen, otherwise check for OpenAI, then use mock
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if dashscope_api_key and dashscope_api_key != "your_dashscope_api_key_here":
            # Use Qwen model
            self.llm = QwenChatModel(model_name="qwen-max", temperature=0.7)
        elif openai_api_key and openai_api_key != "your_openai_api_key_here":
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
        else:
            # Use mock LLM for testing
            self.llm = MockChatOpenAI()
        
        # Initialize daily schedule and personal memory
        self.daily_schedule = {}
        self.personal_memory = ConversationMemory(max_memories_per_agent=20)
        
        # Initialize combat stats (for future use)
        self.health = 100
        self.strength = 10
        self.defense = 5
        self.experience = 0
        self.level = 1
        
    def get_response(self, prompt: str, agent_context: str = "") -> str:
        """
        Get response from the LLM with memory context and persona information
        """
        # Retrieve relevant memories
        recent_memories = self.memory.get_recent_memories(self.name, limit=5)
        long_term_memories = self.memory.get_long_term_memories(self.name, limit=10)
        
        # Construct persona context if available
        persona_context = ""
        if self.persona:
            traits = ", ".join(self.personality_traits)
            behavioral_patterns = ", ".join(self.behavioral_patterns)
            persona_context = f"""
Personality traits: {traits or 'None specified'}
Communication style: {self.communication_style or 'Not specified'}
Behavioral patterns: {behavioral_patterns or 'None specified'}
"""
        
        # Construct the full prompt with context
        context = f"Agent Context: {agent_context}\n" if agent_context else ""
        recent_memory_context = "\n".join([f"- {memory}" for memory in recent_memories])
        long_term_memory_context = "\n".join([f"- (Long-term) {memory}" for memory in long_term_memories])
        
        full_prompt = f"""
{context}
{persona_context}

Recent memories: {recent_memory_context or 'No recent memories'}

Long-term memories: {long_term_memory_context or 'No long-term memories'}

Current conversation: {prompt}

As {self.name}, respond to the above conversation.
"""
        
        # Create system message with persona information
        system_content = f"你是{self.name}，一个在模拟世界中的AI代理，可以访问你的记忆。"
        if self.persona:
            system_content += f" 你的角色是{self.role}。"
            if self.personality_traits:
                system_content += f" 你的性格特征包括：{', '.join(self.personality_traits)}。"
            if self.behavioral_patterns:
                system_content += f" 你倾向于：{', '.join(self.behavioral_patterns)}。"
            if self.communication_style:
                system_content += f" 你的沟通风格是{self.communication_style}。"
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=full_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def remember(self, event: str, memory_type: str = "conversation", location: str = None):
        """
        Add an event to memory
        """
        # Use the agent's current location if no location is specified
        if location is None:
            location = getattr(self, 'location', 'unknown')
        self.memory.add_memory(self.name, event, memory_type, location=location)
    
    def remember_long_term(self, event: str, memory_type: str = "long_term"):
        """
        Explicitly add an event to long-term memory
        """
        # Add to regular memory first, which will automatically move to long-term if limit is reached
        self.memory.add_memory(self.name, event, memory_type)
    
    def search_memories(self, query: str) -> List[Dict]:
        """
        Search for specific memories containing the query
        """
        return self.memory.search_memories(self.name, query)
    
    def get_all_memories(self) -> List[Dict]:
        """
        Get all memories (both short and long term) for this agent
        """
        return self.memory.get_all_memories(self.name)
    
    def get_memory_summary(self) -> str:
        """
        Get a summary of this agent's memories
        """
        all_memories = self.memory.get_all_memories(self.name)
        short_term_memories = self.memory.get_recent_memories(self.name, limit=100)  # Get all recent memories
        long_term_count = len(all_memories) - len(short_term_memories)
        
        return f"{self.name} has {len(short_term_memories)} recent memories and {long_term_count} long-term memories."
    
    def clear_memories(self):
        """
        Clear all memories for this agent (move to long-term first)
        """
        self.memory.clear_agent_memories(self.name)
    
    def save_memories_to_file(self, filename: str = None):
        """
        Save long-term memories to a JSON file
        """
        if filename is None:
            filename = f"memories_{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            all_memories = self.memory.get_all_memories(self.name)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "agent_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "memories": all_memories
                }, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(all_memories)} memories for {self.name} to {filename}")
            return True
        except Exception as e:
            print(f"Error saving memories to {filename}: {e}")
            return False
    
    def load_memories_from_file(self, filename: str):
        """
        Load memories from a JSON file
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "memories" in data:
                # Add each memory back to the agent's memory system
                for memory in data["memories"]:
                    self.memory.add_memory(
                        self.name, 
                        memory["content"], 
                        memory.get("type", "conversation")
                    )
                print(f"Loaded {len(data['memories'])} memories for {self.name} from {filename}")
                return True
            else:
                print(f"No memories found in {filename}")
                return False
        except Exception as e:
            print(f"Error loading memories from {filename}: {e}")
            return False
    
    def schedule_event(self, title: str, start_time, end_time, description: str = "", location: str = ""):
        """
        Schedule an event for this agent
        """
        return self.world.schedule_event(self.name, title, start_time, end_time, description, location)
    
    def get_upcoming_events(self, hours: int = 24):
        """
        Get upcoming events for this agent
        """
        return self.world.get_upcoming_events(self.name, hours)
    
    def get_calendar_summary(self):
        """
        Get calendar summary for this agent
        """
        return self.world.get_calendar_summary(self.name)
    
    def schedule_meeting(self, other_agents: List['BaseAgent'], title: str, start_time, end_time, description: str = "", location: str = ""):
        """
        Schedule a meeting with other agents
        """
        participants = [self.name] + [agent.name for agent in other_agents]
        return self.world.schedule_meeting(participants, title, start_time, end_time, description, location)
    
    def move_to_location(self, location: str):
        """
        Move the agent to a specific location in the world
        """
        # Check if location exists in the world map
        if location not in self.world.locations:
            print(f"Warning: {location} does not exist in the world map. Moving to default location instead.")
            location = "classroom"  # Use a default location that exists
            if location not in self.world.locations:
                # If classroom doesn't exist, pick any existing location
                location = list(self.world.locations.keys())[0]
        
        # Remove agent from current location if already in the world
        if hasattr(self, 'name'):
            current_location_agents = self.world.get_agents_at_location(self.location)
            if self in current_location_agents:
                self.world.remove_agent_from_location(self, self.location)
        
        # Add agent to new location
        self.world.add_agent_to_location(self, location)
        self.location = location
        self.remember(f"Moved to {location}", "movement", location=location)
        return f"{self.name} moved to {location}"
    
    def get_agents_at_current_location(self):
        """
        Get all other agents at the current location
        """
        agents_at_location = self.world.get_agents_at_location(self.location)
        # Exclude self from the list
        return [agent for agent in agents_at_location if agent != self]
    
    def talk_to_agents_at_location(self, topic: str = None):
        """
        Initiate conversation with all other agents at the same location
        """
        other_agents = self.get_agents_at_current_location()
        
        if not other_agents:
            print(f"{self.name} is alone at {self.location}. No one to talk to.")
            return []
        
        if topic is None:
            topic = "general conversation"
        
        conversation_results = []
        
        # Start a conversation with all agents at the location
        agent_names = [agent.name for agent in other_agents]
        print(f"\n{self.name} starts a conversation with {', '.join(agent_names)} at {self.location} about '{topic}':")
        
        # Self speaks first
        prompt = f"Start a conversation about {topic} with {agent_names} at {self.location}."
        response = self.get_response(prompt, f"You are {self.name} initiating a conversation.")
        print(f"{self.name}: {response}")
        conversation_results.append((self.name, response))
        
        # Other agents respond
        for agent in other_agents:
            prompt = f"Respond to {self.name}'s conversation about {topic} at {self.location}."
            response = agent.get_response(prompt, f"You are {agent.name} responding in the conversation.")
            print(f"{agent.name}: {response}")
            conversation_results.append((agent.name, response))
            
            # Remember the interaction for both agents
            self.remember(f"Talked to {agent.name} about {topic} at {self.location}", "conversation")
            agent.remember(f"Talked to {self.name} about {topic} at {self.location}", "conversation")
        
        return conversation_results
    
    @abstractmethod
    def interact(self, other_agents: List['BaseAgent'], topic: str = None):
        pass

    def create_daily_schedule(self, date: str, total_schedule_logic: Dict = None):
        """
        Create a daily schedule based on total schedule logic, personal preferences, 
        memories, and map information
        """
        if total_schedule_logic is None:
            total_schedule_logic = {}
        
        # Get agent's preferences and memories
        preferences = {
            "personality_traits": self.personality_traits,
            "schedule_preferences": self.schedule_preferences,
            "preferred_locations": self.preferred_locations,
            "learning_goals": self.learning_goals if hasattr(self, 'learning_goals') else [],
            "social_preferences": getattr(self, 'social_preferences', []),
            "activity_preferences": getattr(self, 'activity_preferences', [])
        }
        
        # Get recent memories to influence the schedule
        recent_memories = self.personal_memory.get_recent_memories(self.name, limit=10)
        
        # Create schedule based on total schedule logic and personal preferences
        schedule = {}
        
        for period in total_schedule_logic.get("time_periods", ["morning_class", "morning_free", "afternoon_class", "afternoon_free", "evening"]):
            schedule_logic = total_schedule_logic.get("schedule_logic", {}).get(period, {})
            
            # Determine if this is a required activity
            if schedule_logic.get("required", False):
                # Required activity - follow the schedule logic
                location = schedule_logic.get("location", "classroom")
                activity = schedule_logic.get("activity", "attend_class")
                
                # Add probability factor
                probability = schedule_logic.get("probability", 1.0)
                if random.random() <= probability:
                    schedule[period] = {
                        "location": location,
                        "activity": activity,
                        "required": True
                    }
                else:
                    # If not following required activity, use personal preferences
                    preferred_location = random.choice(self.preferred_locations) if self.preferred_locations else "classroom"
                    schedule[period] = {
                        "location": preferred_location,
                        "activity": "personal_activity",
                        "required": False
                    }
            else:
                # Optional activity - use personal preferences
                preferred_location = random.choice(self.preferred_locations) if self.preferred_locations else "classroom"
                possible_activities = [
                    "study", "socialize", "explore", "rest", "reflect", 
                    "practice", "research", "create", "think"
                ]
                
                # Adjust activities based on personality and goals
                if "social" in str(self.personality_traits):
                    possible_activities.extend(["socialize", "discuss", "collaborate"] * 2)
                if "analytical" in str(self.personality_traits):
                    possible_activities.extend(["study", "analyze", "review"] * 2)
                if "creative" in str(self.personality_traits):
                    possible_activities.extend(["create", "explore", "innovate"] * 2)
                
                activity = random.choice(possible_activities)
                
                schedule[period] = {
                    "location": preferred_location,
                    "activity": activity,
                    "required": False
                }
        
        self.daily_schedule[date] = schedule
        return schedule

    def start_conversation(self, other_agents: List['BaseAgent'], topic: str, max_rounds: int = 5, conversation_type: str = "multi"):
        """
        Start a multi-round conversation with other agents
        """
        conversation_history = []
        
        # Check if agents want to join the conversation based on their schedules and personalities
        participating_agents = []
        for agent in other_agents:
            # Agent decides whether to join based on their personality, schedule, and memory
            should_join = self._should_join_conversation(agent, topic)
            if should_join:
                participating_agents.append(agent)
        
        # Add self to the conversation
        participating_agents.insert(0, self)
        
        if len(participating_agents) < 2:
            # Not enough agents for a conversation
            self.remember(f"Tried to start a conversation about '{topic}' but not enough agents joined", "conversation", location=self.location)
            return conversation_history
        
        print(f"\nStarting {conversation_type} conversation about '{topic}' with {len(participating_agents)} agents at {self.location}: {[agent.name for agent in participating_agents]}")
        
        # Conduct the conversation for max_rounds
        for round_num in range(max_rounds):
            print(f"\n--- Round {round_num + 1} ---")
            
            for agent in participating_agents:
                # Generate agent's response based on conversation history and topic
                conversation_context = "\n".join([f"{entry['agent']}: {entry['message']}" for entry in conversation_history[-5:]])
                
                prompt = f"""
                You are {agent.name} participating in a conversation about '{topic}'.
                Previous conversation:
                {conversation_context}
                
                Respond to the conversation, keeping in mind your personality traits: {', '.join(agent.personality_traits)}.
                """
                
                response = agent.get_response(prompt, f"You are participating in a conversation about '{topic}'.")
                print(f"{agent.name}: {response}")
                
                # Add to conversation history
                conversation_history.append({
                    "agent": agent.name,
                    "message": response,
                    "round": round_num + 1,
                    "topic": topic
                })
                
                # Remember the interaction
                agent.remember(f"Participated in conversation about '{topic}' with {[a.name for a in participating_agents if a != agent]}", "conversation", location=agent.location)
        
        # Create a long-term memory of the conversation
        conversation_summary = f"Had a {max_rounds}-round conversation about '{topic}' with {[a.name for a in participating_agents[1:]]}"
        for agent in participating_agents:
            agent.remember_long_term(conversation_summary, "conversation")
        
        return conversation_history

    def _should_join_conversation(self, agent, topic: str):
        """
        Determine if an agent should join a conversation based on their personality, 
        schedule, and memory
        """
        # Check if agent is available (not in a required activity)
        current_time_period = "current_period"  # This would be determined by the simulation
        # For now, assume they're available if they're at the same location
        at_same_location = agent.location == self.location
        
        # Check social preferences
        social_willingness = "collaborate" in getattr(agent, 'social_preferences', []) or \
                            "discuss" in getattr(agent, 'social_preferences', []) or \
                            "network" in getattr(agent, 'social_preferences', [])
        
        # Check personality traits
        extroversion = "social" in agent.personality_traits or \
                      "expressive" in agent.personality_traits or \
                      "collaborative" in agent.personality_traits
        
        # If the topic is related to their learning goals or interests
        topic_relevance = any(goal in topic.lower() for goal in getattr(agent, 'learning_goals', [])) or \
                         any(pref in topic.lower() for pref in getattr(agent, 'activity_preferences', []))
        
        # Calculate probability of joining
        base_probability = 0.5
        if social_willingness:
            base_probability += 0.2
        if extroversion:
            base_probability += 0.2
        if topic_relevance:
            base_probability += 0.3
        if not at_same_location:
            base_probability -= 0.5  # Much less likely if not at same location
        
        # Cap between 0 and 1
        join_probability = max(0, min(1, base_probability))
        
        return random.random() < join_probability

    def start_battle(self, opponent: 'BaseAgent'):
        """
        Simulate a battle between this agent and an opponent
        """
        print(f"\nBattle started between {self.name} and {opponent.name} at {self.location}!")
        
        # Store initial stats
        initial_self_health = self.health
        initial_opponent_health = opponent.health
        
        # Battle rounds
        round_num = 1
        battle_log = []
        
        while self.health > 0 and opponent.health > 0:
            print(f"\n--- Battle Round {round_num} ---")
            
            # Self attacks opponent
            damage_to_opponent = max(1, self.strength - opponent.defense + random.randint(-2, 3))
            opponent.health -= damage_to_opponent
            print(f"{self.name} attacks {opponent.name} for {damage_to_opponent} damage!")
            
            if opponent.health <= 0:
                opponent.health = 0
                battle_log.append(f"Round {round_num}: {self.name} attacks {opponent.name} for {damage_to_opponent} damage. {opponent.name} is defeated!")
                break
            
            # Opponent attacks self
            damage_to_self = max(1, opponent.strength - self.defense + random.randint(-2, 3))
            self.health -= damage_to_self
            print(f"{opponent.name} attacks {self.name} for {damage_to_self} damage!")
            
            if self.health <= 0:
                self.health = 0
                battle_log.append(f"Round {round_num}: {opponent.name} attacks {self.name} for {damage_to_self} damage. {self.name} is defeated!")
                break
            
            battle_log.append(f"Round {round_num}: {self.name} vs {opponent.name} - {self.name} HP: {self.health}, {opponent.name} HP: {opponent.health}")
            
            round_num += 1
            
            # Limit rounds to prevent infinite battles
            if round_num > 10:
                battle_log.append("Battle ended in a draw due to round limit.")
                break
        
        # Determine winner
        if self.health > 0:
            winner = self
            loser = opponent
            print(f"\n{self.name} wins the battle!")
        elif opponent.health > 0:
            winner = opponent
            loser = self
            print(f"\n{opponent.name} wins the battle!")
        else:
            print(f"\nBattle ended in a draw!")
            winner = None
            loser = None
        
        # Generate battle summary and create long-term memory
        battle_summary = f"Battle between {self.name} and {opponent.name} at {self.location}. "
        if winner:
            battle_summary += f"{winner.name} won. "
        else:
            battle_summary += "It was a draw. "
        battle_summary += f"Started with {self.name}: {initial_self_health} HP vs {opponent.name}: {initial_opponent_health} HP."
        
        # Add battle memories to both agents
        self.remember_long_term(battle_summary, "battle")
        opponent.remember_long_term(battle_summary, "battle")
        
        # Restore health after battle
        self.health = 100
        opponent.health = 100
        
        return {
            "winner": winner.name if winner else "draw",
            "battle_log": battle_log,
            "summary": battle_summary
        }