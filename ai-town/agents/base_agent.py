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
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator, persona_id: str = None, agent_type: str = "student"):
        self.memory = memory
        self.world = world
        self.location = "default"  # Default location
        
        # Initialize knowledge manager based on agent type
        from memory.knowledge_base import AgentKnowledgeManager
        self.knowledge_manager = AgentKnowledgeManager(agent_type)
        
        # Load persona if provided, otherwise use default values
        if persona_id and persona_manager.get_persona(persona_id):
            self.persona = persona_manager.get_persona(persona_id)
            self.name = self.persona.get("name", name)
            self.role = self.persona.get("role", "Agent")
            self.personality_traits = self.persona.get("personality_traits", [])
            self.communication_style = self.persona.get("communication_style", "neutral")
            self.behavioral_patterns = self.persona.get("behavioral_patterns", [])
            self.default_responses = self.persona.get("default_responses", {})
        else:
            # Default values if no persona is provided
            self.persona = None
            self.name = name
            self.role = "Agent"
            self.personality_traits = []
            self.communication_style = "neutral"
            self.behavioral_patterns = []
            self.default_responses = {}
        
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
        system_content = f"You are {self.name}, an AI agent in a simulated world with access to your memories."
        if self.persona:
            system_content += f" Your role is {self.role}."
            if self.personality_traits:
                system_content += f" Your personality traits include: {', '.join(self.personality_traits)}."
            if self.behavioral_patterns:
                system_content += f" You tend to: {', '.join(self.behavioral_patterns)}."
            if self.communication_style:
                system_content += f" Your communication style is {self.communication_style}."
        
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