import json
import random
from typing import Dict, List, Any, Optional, Tuple
from memory.memory_manager import MemoryManager


class BaseAgent:
    def __init__(self, config_path: str, memory_manager: MemoryManager, world_manager):
        self.config_path = config_path
        self.memory_manager = memory_manager
        self.world_manager = world_manager
        self.config = {}
        self.name = ""
        self.persona = ""
        self.is_expert = False
        self.dialogue_style = ""
        self.schedule_habits = {}
        self.作息习惯 = ""
        self.current_location = ""
        self.long_term_memories = []
        self.dialogue_memory = []
        
        self.load_config()
    
    def load_config(self):
        """Load agent configuration from JSON file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.name = self.config.get("name", "")
        self.persona = self.config.get("persona", "")
        self.is_expert = self.config.get("is_expert", False)
        self.dialogue_style = self.config.get("dialogue_style", "")
        self.schedule_habits = self.config.get("schedule_habits", {})
        self.作息习惯 = self.config.get("作息习惯", "")
        
        # Initialize position based on world manager
        self.current_location = self.world_manager.agents_positions.get(self.name, "unknown")
    
    def update_location(self, new_location: str):
        """Update agent's location in the world"""
        if self.world_manager.move_agent(self.name, new_location):
            self.current_location = new_location
            return True
        return False
    
    def get_daily_schedule(self, day: int, period: str) -> str:
        """Generate a daily schedule based on persona, habits, and world schedule"""
        world_schedule = self.world_manager.get_current_schedule(day, period)
        
        # Check if this agent is required to do something specific
        if self.name in world_schedule.get("required", []):
            return world_schedule["default"]
        
        # Otherwise, follow personal habits if they exist
        personal_habit = self.schedule_habits.get(period)
        if personal_habit:
            return personal_habit
        
        # Default to world schedule if no personal habit
        return world_schedule["default"]
    
    def generate_memory_from_event(self, event_description: str, event_type: str = "event") -> int:
        """Generate a memory from an event"""
        return self.memory_manager.add_memory(
            agent_name=self.name,
            content=event_description,
            memory_type=event_type,
            related_agents=[self.name]  # By default, only this agent is involved
        )
    
    def recall_memories(self, query: str = "", memory_type: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """Recall relevant memories"""
        return self.memory_manager.search_memories(
            agent_name=self.name,
            query=query,
            memory_type=memory_type,
            limit=limit
        )
    
    def participate_in_conversation(self, participants: List[str], topic: str, max_rounds: int) -> List[Dict[str, str]]:
        """Participate in a multi-round conversation"""
        conversation = []
        
        # Check if agent wants to participate based on persona and schedule
        if not self.should_join_conversation(topic):
            # Agent chooses not to join, returns empty conversation
            return conversation
        
        # Initialize conversation with first message
        first_message = self.generate_conversation_message(topic, conversation, is_first=True)
        conversation.append({"agent": self.name, "message": first_message})
        
        # Continue conversation for max_rounds or until topic is exhausted
        for _ in range(1, max_rounds):
            # Get response from this agent
            response = self.generate_conversation_message(topic, conversation)
            conversation.append({"agent": self.name, "message": response})
            
            # In a real implementation, other agents would also contribute
            # For now, we simulate this with a placeholder
            break  # Simplified for this implementation
        
        # Generate memory from this conversation
        conversation_summary = f"Participated in conversation about '{topic}' with {', '.join(participants)}"
        self.generate_memory_from_event(conversation_summary, "conversation")
        
        return conversation
    
    def should_join_conversation(self, topic: str) -> bool:
        """Determine if agent should join a conversation based on persona and current schedule"""
        # Implement logic based on persona and current activities
        # For now, a simple implementation
        return True
    
    def generate_conversation_message(self, topic: str, conversation_history: List[Dict[str, str]], 
                                     is_first: bool = False) -> str:
        """Generate a message for a conversation"""
        # This would typically use LLM to generate a response based on persona
        # For now, we'll return a placeholder
        if is_first:
            return f"Hello, I'm interested in discussing {topic}. {self.persona.split('.')[0]}."
        else:
            return f"My perspective on {topic} is that it's quite interesting. {random.choice(['I think', 'In my opinion', 'From my understanding'])}..."
    
    def engage_in_battle(self, opponent: 'BaseAgent') -> Dict[str, Any]:
        """Simulate a battle with another agent"""
        # Simulate a simple battle outcome
        battle_outcome = {
            "participants": [self.name, opponent.name],
            "winner": self.name if random.random() > 0.5 else opponent.name,
            "summary": f"{self.name} battled with {opponent.name} and {'won' if random.random() > 0.5 else 'lost'}",
            "duration": random.randint(5, 15)  # minutes
        }
        
        # Generate long-term memory from battle
        self.generate_memory_from_event(battle_outcome["summary"], "battle")
        opponent.generate_memory_from_event(battle_outcome["summary"], "battle")
        
        return battle_outcome
    
    def act_independently(self, activity: str) -> str:
        """Perform an independent activity and generate a memory"""
        # Simulate an independent activity
        result = f"{self.name} performed {activity} at {self.current_location}"
        
        # Generate memory from this activity
        self.generate_memory_from_event(result, "independent_activity")
        
        return result
    
    def get_nearby_agents(self) -> List[str]:
        """Get list of agents at the same location"""
        return self.world_manager.get_agents_at_location(self.current_location)
    
    def plan_daily_activities(self, day: int) -> Dict[str, str]:
        """Plan activities for the entire day based on schedule and persona"""
        daily_plan = {}
        time_periods = ["morning_1", "morning_2", "afternoon_1", "afternoon_2", "evening"]
        
        for period in time_periods:
            daily_plan[period] = self.get_daily_schedule(day, period)
        
        return daily_plan