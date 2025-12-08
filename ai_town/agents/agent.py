import json
import os
import jsonlines
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi
from ..memory.memory_manager import MemoryManager
from ..configs.config_loader import ConfigLoader


class AgentConfig(BaseModel):
    name: str
    role: str
    is_expert: bool
    personality: str
    dialogue_style: str
    schedule_habits: List[str]
    knowledge_base_access: bool
    teaching_subject: Optional[str] = None


class Agent:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.name = self.config.name
        self.role = self.config.role
        self.is_expert = self.config.is_expert
        self.personality = self.config.personality
        self.dialogue_style = self.config.dialogue_style
        self.schedule_habits = self.config.schedule_habits
        self.knowledge_base_access = self.config.knowledge_base_access
        self.teaching_subject = self.config.teaching_subject
        
        # Initialize LLM
        config_data = ConfigLoader.load_config('config')
        self.llm = ChatTongyi(
            model_name=config_data['model_name'],
            dashscope_api_key=config_data['api_key'],
            temperature=config_data['llm_config']['temperature']
        )
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(self.name)
        
        # Current position
        self.current_location = "dormitory"  # Default starting location
        
        # Daily schedule for the agent
        self.daily_schedule = {}
        
    def load_config(self, config_file: str) -> AgentConfig:
        """Load agent configuration from JSON file"""
        with open(f"/workspace/ai_town/configs/{config_file}", 'r') as f:
            data = json.load(f)
        return AgentConfig(**data)
    
    def create_daily_schedule(self, day_num: int, total_days: int, world_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a daily schedule based on persona, world info, and previous memories
        """
        # Get current date context
        date_context = f"Day {day_num} of {total_days}"
        
        # Retrieve recent memories to inform decision making
        recent_memories = self.memory_manager.search_memories("recent_activities", limit=5)
        
        # Get map information
        map_info = world_info.get('map', {})
        locations = [loc['name'] for loc in map_info.get('locations', [])]
        
        # Get current day's global schedule
        daily_schedule = world_info.get('schedule', {}).get('daily_schedule', {})
        
        # Prepare prompt for schedule creation
        prompt = f"""
        As {self.name}, a {self.role}, create your daily schedule for {date_context}.
        
        PERSONA:
        - Personality: {self.personality}
        - Schedule habits: {', '.join(self.schedule_habits)}
        
        WORLD INFORMATION:
        - Locations available: {', '.join(locations)}
        - Global schedule for today: {daily_schedule}
        
        PREVIOUS MEMORIES:
        {recent_memories}
        
        Create a schedule that aligns with your persona and habits while respecting the global schedule.
        Return a dictionary mapping time periods to activities and locations.
        
        Time periods are: morning_1, morning_2, afternoon_1, afternoon_2, evening
        Each activity should specify both the activity type and the location.
        """
        
        # Generate schedule using LLM
        try:
            response = self.llm.invoke(prompt)
            # Parse the response to get the schedule
            # In a real implementation, we would parse the structured response properly
            # For now, we'll simulate a basic schedule
            schedule = {
                "morning_1": {"activity": "attend_class", "location": "classroom"},
                "morning_2": {"activity": "study", "location": "library"},
                "afternoon_1": {"activity": "attend_class", "location": "classroom"},
                "afternoon_2": {"activity": "personal_activity", "location": "playground"},
                "evening": {"activity": "rest", "location": "dormitory"}
            }
            
            # Update the schedule based on persona and habits
            for period, details in schedule.items():
                if period == "evening":
                    schedule[period]["location"] = "dormitory"
                elif "class" in details["activity"]:
                    schedule[period]["location"] = "classroom"
                elif "study" in details["activity"]:
                    schedule[period]["location"] = "library"
            
            self.daily_schedule = schedule
            return schedule
            
        except Exception as e:
            print(f"Error generating schedule for {self.name}: {e}")
            # Fallback to a default schedule
            return {
                "morning_1": {"activity": "attend_class", "location": "classroom"},
                "morning_2": {"activity": "study", "location": "library"},
                "afternoon_1": {"activity": "attend_class", "location": "classroom"},
                "afternoon_2": {"activity": "personal_activity", "location": "playground"},
                "evening": {"activity": "rest", "location": "dormitory"}
            }
    
    def move_to_location(self, location: str) -> bool:
        """
        Request to move to a specific location in the world
        """
        self.current_location = location
        self.memory_manager.add_memory({
            "type": "movement",
            "timestamp": datetime.now().isoformat(),
            "action": f"moved to {location}",
            "location": location
        })
        return True
    
    def initiate_dialogue(self, participants: List[str], topic: str, max_rounds: int) -> List[Dict[str, str]]:
        """
        Initiate a multi-round dialogue with other agents
        """
        dialogue_history = []
        
        # Check if I want to participate based on my persona and schedule
        if not self.should_participate_in_dialogue(topic):
            # If I don't join, I still generate my own activity
            self.memory_manager.add_memory({
                "type": "independent_activity",
                "timestamp": datetime.now().isoformat(),
                "activity": f"focused on personal task instead of dialogue about {topic}",
                "location": self.current_location
            })
            return dialogue_history
        
        # Simulate dialogue rounds
        for round_num in range(max_rounds):
            # Generate my response based on persona and topic
            response_prompt = f"""
            As {self.name} ({self.role}), respond to the dialogue about '{topic}'.
            
            PERSONA:
            - Personality: {self.personality}
            - Dialogue style: {self.dialogue_style}
            
            DIALOGUE HISTORY:
            {dialogue_history[-3:] if len(dialogue_history) > 3 else dialogue_history}
            
            What would you say next?
            """
            
            try:
                response = self.llm.invoke(response_prompt)
                dialogue_history.append({
                    "speaker": self.name,
                    "message": response.content,
                    "round": round_num + 1
                })
                
                # Add to memory
                self.memory_manager.add_memory({
                    "type": "dialogue_participation",
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic,
                    "participants": participants,
                    "round": round_num + 1,
                    "message": response.content
                })
                
            except Exception as e:
                print(f"Error generating dialogue response for {self.name}: {e}")
                break
                
        return dialogue_history
    
    def should_participate_in_dialogue(self, topic: str) -> bool:
        """
        Determine if the agent should participate in a dialogue based on persona and schedule
        """
        # Simple heuristic: participate if topic is interesting or related to responsibilities
        if self.is_expert and self.teaching_subject and self.teaching_subject.lower() in topic.lower():
            return True
        
        # Students might participate based on their interests
        if "math" in topic.lower() or "study" in topic.lower():
            return True
            
        return True  # For simplicity, assume participation unless explicitly not wanted
    
    def engage_in_battle(self, opponent: str) -> Dict[str, Any]:
        """
        Engage in a simulated battle with another agent
        """
        # This is a simulation - in a real implementation, this would have more complex logic
        battle_result = {
            "participants": [self.name, opponent],
            "winner": self.name if hash(self.name) % 2 == 0 else opponent,
            "duration": "short",
            "summary": f"{self.name} had a friendly competition with {opponent}"
        }
        
        # Add battle result to memory as a long-term memory
        self.memory_manager.add_memory({
            "type": "battle",
            "timestamp": datetime.now().isoformat(),
            "result": battle_result,
            "participants": [self.name, opponent]
        }, long_term=True)
        
        return battle_result
    
    def update_from_world_state(self, world_state: Dict[str, Any]):
        """
        Update agent's internal state based on world state
        """
        # Agent can update its understanding based on world events
        pass
    
    def generate_long_term_memory(self, events: List[Dict[str, Any]]):
        """
        Generate a long-term memory entry from recent events
        """
        if not events:
            return
            
        # Summarize recent events
        event_summaries = [f"{event.get('type', 'unknown')}: {event}" for event in events[:5]]
        
        summary_prompt = f"""
        As {self.name}, create a concise summary of these recent events in your life:
        {chr(10).join(event_summaries)}
        
        Focus on the most important aspects that should be remembered long-term.
        """
        
        try:
            response = self.llm.invoke(summary_prompt)
            
            # Add to long-term memory
            self.memory_manager.add_memory({
                "type": "long_term_summary",
                "timestamp": datetime.now().isoformat(),
                "summary": response.content,
                "source_events": [event.get('type', 'unknown') for event in events[:5]]
            }, long_term=True)
            
        except Exception as e:
            print(f"Error generating long-term memory for {self.name}: {e}")