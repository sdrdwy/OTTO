import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import Tongyi
from memory.long_term_memory import LongTermMemory
from world.world_manager import WorldManager


class BaseAgent:
    def __init__(self, config_path: str):
        # Load agent configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.name = self.config['name']
        self.role = self.config['role']
        self.is_expert = self.config['is_expert']
        self.personality = self.config['personality']
        self.schedule_preferences = self.config['schedule_preferences']
        self.knowledge_base_access = self.config['knowledge_base_access']
        self.dialogue_preferences = self.config['dialogue_preferences']
        self.作息习惯 = self.config['作息习惯']
        
        # Initialize LLM
        self.llm = Tongyi(
            model_name="qwen-max",
            temperature=0.7,
            api_key=os.getenv("DASHSCOPE_API_KEY", "your_dashscope_api_key_here")
        )
        
        # Initialize memory
        self.memory = LongTermMemory(self.name)
        
        # Initialize world manager
        self.world_manager = WorldManager()
        
        # Agent state
        self.location = "dormitory"  # Default starting location
        self.current_schedule = {}
        self.exam_scores = {}
        
    def get_system_prompt(self) -> str:
        """Generate system prompt based on agent's personality and role"""
        traits = ", ".join(self.personality['traits'])
        patterns = ", ".join(self.personality['behavioral_patterns'])
        
        return f"""
        You are {self.name}, a {self.role} in a simulated educational environment.
        Your personality traits are: {traits}.
        Your behavioral patterns include: {patterns}.
        Your communication style is: {self.personality['communication_style']}.
        Respond in character, considering your personality and role.
        """
    
    def generate_daily_schedule(self, date: str, map_info: Dict, previous_memories: List[Dict]) -> Dict:
        """Generate a daily schedule based on persona, map info, and memories"""
        # This will be implemented by subclasses
        pass
    
    def move_to_location(self, location: str) -> bool:
        """Request to move to a specific location"""
        return self.world_manager.move_agent(self.name, location)
    
    def initiate_conversation(self, other_agents: List[str], topic: str, max_rounds: int) -> List[Dict]:
        """Initiate a multi-round conversation with other agents"""
        conversation_log = []
        
        # Check if agents are available for conversation
        available_agents = []
        for agent_name in other_agents:
            agent_location = self.world_manager.get_agent_location(agent_name)
            if agent_location == self.location:
                available_agents.append(agent_name)
        
        if not available_agents:
            return conversation_log
        
        # Start conversation
        round_num = 0
        current_topic = topic
        
        while round_num < max_rounds:
            for agent_name in [self.name] + available_agents:
                # Get agent's response based on personality and context
                agent_response = self._get_agent_response(agent_name, current_topic, conversation_log)
                conversation_log.append({
                    "round": round_num + 1,
                    "agent": agent_name,
                    "message": agent_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update topic if needed based on conversation
                current_topic = self._update_topic_if_needed(conversation_log)
            
            round_num += 1
            
            # Check if conversation should continue
            if self._should_end_conversation(conversation_log):
                break
        
        # Create long-term memory from conversation
        conversation_summary = self._summarize_conversation(conversation_log)
        self.memory.add_memory(conversation_summary, "conversation", {"type": "multi_agent_conversation", "participants": [self.name] + available_agents})
        
        return conversation_log
    
    def _get_agent_response(self, agent_name: str, topic: str, conversation_log: List[Dict]) -> str:
        """Get response from an agent during conversation"""
        if agent_name == self.name:
            # Use this agent's LLM
            prompt = f"""
            {self.get_system_prompt()}
            
            Previous conversation:
            {self._format_conversation_log(conversation_log[-5:]) if conversation_log else "No previous conversation"}
            
            Current topic: {topic}
            
            Respond to the conversation as {self.name}.
            """
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Respond to: {topic}")
            ]
            response = self.llm.invoke(messages)
            return response.content
        else:
            # For other agents, we'd need to get their instance - simplified for now
            return f"{agent_name} responds to the topic: {topic}"
    
    def _format_conversation_log(self, log: List[Dict]) -> str:
        """Format conversation log for context"""
        formatted = []
        for entry in log:
            formatted.append(f"{entry['agent']}: {entry['message']}")
        return "\n".join(formatted)
    
    def _update_topic_if_needed(self, conversation_log: List[Dict]) -> str:
        """Update conversation topic based on flow"""
        # For now, keep the same topic, but in a full implementation this would analyze the conversation
        return conversation_log[-1]['message'] if conversation_log else "general conversation"
    
    def _should_end_conversation(self, conversation_log: List[Dict]) -> bool:
        """Determine if conversation should end early"""
        # Simple heuristic: if last few messages are very short, end conversation
        if len(conversation_log) >= 3:
            recent_messages = conversation_log[-3:]
            short_message_count = sum(1 for msg in recent_messages if len(msg['message']) < 10)
            if short_message_count >= 2:
                return True
        return False
    
    def _summarize_conversation(self, conversation_log: List[Dict]) -> str:
        """Create a summary of the conversation for long-term memory"""
        participants = list(set(entry['agent'] for entry in conversation_log))
        topic = conversation_log[0]['message'] if conversation_log else "general conversation"
        return f"Had a {len(conversation_log)}-round conversation with {', '.join(participants[1:])} about {topic[:50]}..."
    
    def participate_in_conversation(self, conversation_request: Dict) -> bool:
        """Decide whether to join a multi-agent conversation"""
        # Based on agent's personality, schedule, and memories
        # Check if agent is interested in the topic or likes the participants
        topic = conversation_request.get('topic', '')
        participants = conversation_request.get('participants', [])
        
        # Check if topic aligns with agent's interests
        preferred_topics = self.dialogue_preferences.get('preferred_topics', [])
        is_topic_interesting = any(pref_topic in topic.lower() for pref_topic in preferred_topics)
        
        # Check if agent is free at current time/location
        is_available = self.location == conversation_request.get('location', self.location)
        
        # Make decision based on personality and preferences
        personality_traits = self.personality['traits']
        is_social = 'collaborative' in personality_traits or 'outgoing' in personality_traits
        
        return is_available and (is_topic_interesting or is_social)
    
    def battle(self, opponent: str) -> Dict:
        """Simulate a battle with another agent"""
        # For now, this is a simple simulation - in a full implementation this would be more complex
        result = {
            "participants": [self.name, opponent],
            "winner": self.name if hash(self.name) % 10 > hash(opponent) % 10 else opponent,
            "battle_log": [
                {"turn": 1, "action": f"{self.name} attacks {opponent}"},
                {"turn": 2, "action": f"{opponent} defends against {self.name}"},
                {"turn": 3, "action": f"{self.name} wins the battle!" if result["winner"] == self.name else f"{opponent} wins the battle!"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Create long-term memory from battle
        battle_summary = f"Engaged in battle with {opponent}. {result['winner']} won the battle."
        self.memory.add_memory(battle_summary, "battle", {"opponent": opponent, "result": result["winner"]})
        
        return result
    
    def generate_memory(self, event: str, memory_type: str = "experience") -> None:
        """Generate a memory from an event"""
        self.memory.add_memory(event, memory_type, {"location": self.location, "timestamp": datetime.now().isoformat()})
    
    def get_local_agents(self) -> List[str]:
        """Get list of other agents at current location"""
        return self.world_manager.get_agents_at_location(self.location)
    
    def get_agent_info(self) -> Dict:
        """Get agent information"""
        return {
            "name": self.name,
            "role": self.role,
            "location": self.location,
            "is_expert": self.is_expert
        }