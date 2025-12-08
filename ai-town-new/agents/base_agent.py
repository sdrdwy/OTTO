import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
import uuid


class MemoryEntry(BaseModel):
    id: str
    content: str
    timestamp: str
    importance: float
    metadata: Dict[str, Any]


class BaseAgent:
    def __init__(self, config_path: str):
        # Load agent configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.id = self.config['id']
        self.name = self.config['name']
        self.role = self.config['role']
        self.is_expert = self.config.get('is_expert', False)
        self.personality = self.config['personality']
        self.schedule_habits = self.config['schedule_habits']
        self.knowledge_base_access = self.config.get('knowledge_base_access', False)
        
        # Initialize LLM
        self.llm = ChatTongyi(model="qwen-max", temperature=0.7)
        
        # Initialize memory
        self.memory_file = f"memory/{self.id}_memory.jsonl"
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.long_term_memory = []
        self.conversation_memory = []
        
        # Load existing memory
        self.load_memory()
        
        # Current location
        self.location = "dormitory"  # Default starting location

    def load_memory(self):
        """Load agent's long-term memory from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        memory_data = json.loads(line)
                        memory_entry = MemoryEntry(**memory_data)
                        self.long_term_memory.append(memory_entry)

    def save_memory(self):
        """Save agent's long-term memory to file"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            for memory in self.long_term_memory:
                f.write(json.dumps(memory.dict(), ensure_ascii=False) + '\n')

    def add_memory(self, content: str, importance: float = 0.5, metadata: Dict = None):
        """Add a new memory entry"""
        if metadata is None:
            metadata = {}
        
        memory_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now().isoformat(),
            importance=importance,
            metadata=metadata
        )
        
        self.long_term_memory.append(memory_entry)
        self.save_memory()

    def search_memory(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """Search in long-term memory based on query"""
        # Simple keyword-based search (in a real implementation, you'd use embeddings)
        results = []
        query_lower = query.lower()
        
        for memory in self.long_term_memory:
            if query_lower in memory.content.lower():
                results.append(memory)
        
        # Sort by importance and return top_k
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]

    def generate_daily_schedule(self, date: str, map_info: Dict, other_memories: List[str] = None) -> Dict[str, Any]:
        """Generate a daily schedule based on personality, map info, and memories"""
        if other_memories is None:
            other_memories = []
        
        # Get recent memories as context
        recent_memories = [mem.content for mem in self.long_term_memory[-10:]]
        all_memories = recent_memories + other_memories
        
        # Create prompt for schedule generation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"You are {self.name}, a {self.role}. Your personality: {self.personality['character_setting']}. Your behavior patterns: {', '.join(self.personality['behavior_patterns'])}. Your goals: {', '.join(self.personality['goals'])}. Based on this personality, the map information, and your past memories, create a daily schedule for {date}."),
            HumanMessage(content=f"Map information: {json.dumps(map_info, ensure_ascii=False)}\n\nPast memories: {all_memories}\n\nSchedule habits: {self.schedule_habits}\n\nGenerate a daily schedule for the following time periods: morning_class_1, morning_class_2, afternoon_class_1, afternoon_class_2, evening. For each period, specify the location and activity.")
        ])
        
        # Generate schedule using LLM
        chain = prompt | self.llm
        response = chain.invoke({})
        
        # Parse the response to extract schedule (simplified - in practice you'd use proper parsing)
        # For now, return a default schedule structure
        default_schedule = {
            "date": date,
            "schedule": {
                "morning_class_1": {"location": "classroom", "activity": "attend_class"},
                "morning_class_2": {"location": "classroom", "activity": "attend_class"},
                "afternoon_class_1": {"location": "library", "activity": "study"},
                "afternoon_class_2": {"location": "library", "activity": "practice"},
                "evening": {"location": "dormitory", "activity": "rest"}
            }
        }
        
        return default_schedule

    def move_to_location(self, location: str):
        """Move agent to specified location"""
        self.location = location
        self.add_memory(f"Moved to {location}", importance=0.3, metadata={"action": "movement", "location": location})

    def initiate_dialogue(self, other_agents: List['BaseAgent'], topic: str, max_rounds: int = 5) -> List[Dict[str, str]]:
        """Initiate a multi-round dialogue with other agents"""
        dialogue_history = []
        
        # Check if other agents want to join the dialogue based on their personality and schedule
        participating_agents = [self]
        for agent in other_agents:
            # Simple decision making based on personality and current activity
            should_join = self._should_join_dialogue(agent, topic)
            if should_join:
                participating_agents.append(agent)
        
        # Conduct the dialogue
        for round_num in range(max_rounds):
            for agent in participating_agents:
                # Generate agent's response based on personality and topic
                response = self._generate_dialogue_response(agent, topic, dialogue_history)
                
                dialogue_history.append({
                    "agent": agent.name,
                    "message": response,
                    "round": round_num + 1
                })
                
                # Add to conversation memory
                agent.add_memory(f"Dialogued about '{topic}' with {len(participating_agents)-1} other agents", 
                               importance=0.4, 
                               metadata={"dialogue": True, "topic": topic, "participants": [a.name for a in participating_agents]})
        
        return dialogue_history

    def _should_join_dialogue(self, agent: 'BaseAgent', topic: str) -> bool:
        """Determine if an agent should join a dialogue based on their personality and schedule"""
        # Simplified logic - in practice, this would be more sophisticated
        if agent.name == self.name:  # This agent initiated the dialogue
            return True
            
        # Check if topic aligns with agent's interests
        agent_goals = " ".join(agent.personality['goals']).lower()
        topic_lower = topic.lower()
        
        # Check if agent is currently free or if topic is highly relevant
        if topic_lower in agent_goals:
            return True
            
        # Random factor based on social preferences
        import random
        if 'multiplayer conversations' in agent.schedule_habits['social_preferences']:
            return random.random() > 0.3
        else:
            return random.random() > 0.7

    def _generate_dialogue_response(self, agent: 'BaseAgent', topic: str, dialogue_history: List[Dict]) -> str:
        """Generate a dialogue response for an agent"""
        # Create a prompt for generating the response
        context = f"Previous dialogue: {[entry['message'] for entry in dialogue_history[-3:]]}" if dialogue_history else "No previous dialogue"
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"You are {agent.name}, a {agent.role}. Your personality: {agent.personality['character_setting']}. Your speaking style: {agent.personality['speaking_style']}. Respond to the dialogue topic appropriately based on your personality."),
            HumanMessage(content=f"Topic: {topic}\nContext: {context}\nGenerate a response for the dialogue.")
        ])
        
        chain = prompt | agent.llm
        response = chain.invoke({})
        
        return response.content

    def participate_in_battle(self, opponents: List['BaseAgent']) -> Dict[str, Any]:
        """Participate in a battle simulation"""
        # This is a simplified battle simulation
        # In a real implementation, you'd have a more complex battle system
        battle_log = []
        
        # Simulate battle rounds
        for round_num in range(3):  # 3 rounds
            round_log = {
                "round": round_num + 1,
                "actions": []
            }
            
            for agent in [self] + opponents:
                # Each agent performs an action
                action = f"{agent.name} takes action in battle round {round_num + 1}"
                round_log["actions"].append(action)
                
            battle_log.append(round_log)
        
        # Generate a summary of the battle for long-term memory
        battle_summary = f"Participated in a battle with {[opp.name for opp in opponents]}. Battle lasted {len(battle_log)} rounds."
        self.add_memory(battle_summary, importance=0.8, metadata={"battle": True, "opponents": [opp.name for opp in opponents]})
        
        return {
            "result": "completed",
            "summary": battle_summary,
            "log": battle_log
        }

    def update_memory_weights(self):
        """Update memory weights based on access frequency"""
        # In a real implementation, this would track how often memories are accessed
        # and adjust their importance accordingly
        pass