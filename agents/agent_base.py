import json
import random
from typing import Dict, List, Any, Optional
from memory.memory_manager import MemoryManager
from world.battle_system import BattleSystem


class BaseAgent:
    def __init__(self, config_path: str, memory_manager: MemoryManager):
        self.config = self.load_config(config_path)
        self.name = self.config["name"]
        self.role = self.config["role"]
        self.is_expert = self.config["is_expert"]
        self.personality = self.config["personality"]
        self.dialogue_style = self.config.get("dialogue_style", "")
        self.schedule_preferences = self.config["schedule_preferences"]
        self.作息习惯 = self.config["作息习惯"]
        self.memory_manager = memory_manager
        self.current_location = ""
        self.current_day = 0
        self.current_time_period = ""

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def set_location(self, location: str):
        """Set the agent's current location."""
        self.current_location = location

    def set_day_and_time(self, day: int, time_period: str):
        """Set the current day and time period."""
        self.current_day = day
        self.current_time_period = time_period

    def create_daily_schedule(self, world_info: Dict[str, Any], 
                            mandatory_schedule: Dict[str, str]) -> str:
        """Create a daily schedule based on personal preferences, world info, and mandatory schedule."""
        # Get personal preference for this time period
        personal_preference = self.schedule_preferences.get(self.current_time_period, 
                                                          "No specific preference")
        
        # Check if there's a mandatory activity for this agent
        mandatory_activity = mandatory_schedule.get(self.name, "")
        
        # Decide between mandatory and personal preference based on probability
        schedule_probability = world_info.get("probability", 0.8)
        
        if mandatory_activity and random.random() < schedule_probability:
            return mandatory_activity
        else:
            return personal_preference

    def move_to_location(self, location: str) -> bool:
        """Request to move to a specific location."""
        # In a real implementation, this would communicate with the world manager
        self.current_location = location
        self.memory_manager.add_memory(
            self.name, 
            f"Moved to {location}", 
            "movement"
        )
        return True

    def initiate_dialogue(self, other_agents: List['BaseAgent'], 
                        max_rounds: int, topic: str = "") -> List[Dict[str, str]]:
        """Initiate a multi-round dialogue with other agents."""
        dialogue_history = []
        round_count = 0
        
        # Determine if this agent will participate based on personality and schedule
        if not self.will_participate_in_dialogue():
            # Agent chooses not to participate, generates independent activity
            activity = f"Decided not to join dialogue about '{topic}', instead {self.schedule_preferences.get(self.current_time_period, 'continued with own activities')}"
            self.memory_manager.add_memory(self.name, activity, "activity")
            return dialogue_history
        
        while round_count < max_rounds:
            for agent in other_agents:
                if agent.name != self.name:
                    # Generate a response based on personality and dialogue style
                    response = self.generate_dialogue_response(topic, dialogue_history, agent.name)
                    dialogue_history.append({
                        "speaker": self.name,
                        "listener": agent.name,
                        "message": response,
                        "round": round_count
                    })
                    
                    # Agent's response
                    agent_response = agent.generate_dialogue_response(topic, dialogue_history, self.name)
                    dialogue_history.append({
                        "speaker": agent.name,
                        "listener": self.name,
                        "message": agent_response,
                        "round": round_count
                    })
            
            round_count += 1
            
            # Check if dialogue should end early
            if self.should_end_dialogue(dialogue_history):
                break
        
        # Add dialogue summary to memory
        if dialogue_history:
            summary = f"Participated in dialogue about '{topic}' for {len(dialogue_history)} exchanges"
            self.memory_manager.add_memory(self.name, summary, "dialogue")
        
        return dialogue_history

    def will_participate_in_dialogue(self) -> bool:
        """Determine if the agent will participate in a dialogue based on personality."""
        # More social personalities are more likely to participate
        if "social" in self.personality.lower() or "talkative" in self.personality.lower():
            return random.random() < 0.8
        elif "quiet" in self.personality.lower() or "shy" in self.personality.lower():
            return random.random() < 0.4
        else:
            return random.random() < 0.6

    def generate_dialogue_response(self, topic: str, dialogue_history: List[Dict[str, str]], 
                                 other_agent_name: str) -> str:
        """Generate a dialogue response based on personality and context."""
        # Base response on personality and dialogue style
        base_response = f"{self.name} responds to {other_agent_name} about {topic}."
        return base_response

    def should_end_dialogue(self, dialogue_history: List[Dict[str, str]]) -> bool:
        """Determine if the dialogue should end early."""
        # For now, continue until max rounds unless something specific happens
        return False

    def engage_in_battle(self, opponent: 'BaseAgent') -> Dict[str, Any]:
        """Simulate a battle with another agent."""
        # Use the battle system for more complex battle mechanics
        battle_system = BattleSystem()
        battle_result = battle_system.initiate_battle(self, opponent)
        
        return battle_result

    def generate_long_term_memory(self, event: str):
        """Generate a long-term memory based on an event."""
        self.memory_manager.add_memory(self.name, event, "long_term")