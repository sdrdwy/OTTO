import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage
from memory.conversation_mem import ConversationMemory
from memory.long_term_mem import LongTermMemory
import uuid


class BaseAgent:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.name = self.config["name"]
        self.persona = self.config["persona"]
        self.is_expert = self.config["is_expert"]
        self.dialogue_style = self.config["dialogue_style"]
        self.daily_habits = self.config["daily_habits"]
        self.max_dialogue_rounds = self.config["max_dialogue_rounds"]
        
        # Initialize LLM
        self.llm = ChatTongyi(
            model_name="qwen-max",
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", "sk-c763fc92bf8c46c7ae31639b05d89c96")
        )
        
        # Initialize memories
        self.conversation_memory = ConversationMemory()
        self.long_term_memory = LongTermMemory(f"./memory/{self.name}_long_term.jsonl")
        
        # Agent state
        self.current_location = None
        self.current_schedule = {}
        self.personal_calendar = {}
        
    def set_location(self, location: str):
        """Set agent's current location"""
        self.current_location = location
    
    def get_current_location(self):
        """Get agent's current location"""
        return self.current_location
    
    def create_daily_schedule(self, date: str, world_map: Dict, global_schedule: Dict, personal_memories: List[Dict]):
        """Create daily schedule based on persona, global schedule, map info, and personal memories"""
        system_prompt = f"""
        你是{self.name}，人设：{self.persona}。
        你的对话风格：{self.dialogue_style}。
        你的日常习惯：{self.daily_habits}。
        
        请根据以下信息制定今天的日程安排：
        - 全局日程：{global_schedule}
        - 当前地图信息：{world_map}
        - 个人记忆：{personal_memories}
        
        请返回一个包含以下时间段的日程安排的JSON格式：
        {{
            "morning_1": {{"activity": "活动名称", "location": "地点", "reason": "原因"}},
            "morning_2": {{"activity": "活动名称", "location": "地点", "reason": "原因"}},
            "afternoon_1": {{"activity": "活动名称", "location": "地点", "reason": "原因"}},
            "afternoon_2": {{"activity": "活动名称", "location": "地点", "reason": "原因"}},
            "evening": {{"activity": "活动名称", "location": "地点", "reason": "原因"}}
        }}
        """
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            schedule_text = response.content
            
            # Extract JSON from response
            start_idx = schedule_text.find('{')
            end_idx = schedule_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = schedule_text[start_idx:end_idx]
                self.current_schedule = json.loads(json_str)
            else:
                # Fallback to default schedule if parsing fails
                self.current_schedule = {
                    "morning_1": {"activity": "自习", "location": "图书馆", "reason": "默认安排"},
                    "morning_2": {"activity": "课程", "location": "教室", "reason": "默认安排"},
                    "afternoon_1": {"activity": "自由活动", "location": "公园", "reason": "默认安排"},
                    "afternoon_2": {"activity": "自由活动", "location": "咖啡厅", "reason": "默认安排"},
                    "evening": {"activity": "自由活动", "location": "公园", "reason": "默认安排"}
                }
        except Exception as e:
            print(f"Error creating daily schedule for {self.name}: {e}")
            self.current_schedule = {
                "morning_1": {"activity": "自习", "location": "图书馆", "reason": "默认安排"},
                "morning_2": {"activity": "课程", "location": "教室", "reason": "默认安排"},
                "afternoon_1": {"activity": "自由活动", "location": "公园", "reason": "默认安排"},
                "afternoon_2": {"activity": "自由活动", "location": "咖啡厅", "reason": "默认安排"},
                "evening": {"activity": "自由活动", "location": "公园", "reason": "默认安排"}
            }
        
        return self.current_schedule
    
    def move_to_location(self, world_simulator, location: str):
        """Request to move to a specific location in the world"""
        return world_simulator.move_agent(self.name, location)
    
    def initiate_dialogue(self, participants: List[str], topic: str, max_rounds: int, world_simulator):
        """Initiate a multi-round dialogue with other agents"""
        dialogue_history = []
        
        for round_num in range(max_rounds):
            # Get agents at current location
            current_agents = world_simulator.get_agents_at_location(self.current_location)
            
            # Filter participants who are at the same location and willing to join
            available_participants = []
            for participant in participants:
                if participant in current_agents:
                    # Check if agent is willing to join (based on persona and schedule)
                    participant_agent = world_simulator.get_agent_by_name(participant)
                    if self._should_join_dialogue(participant_agent):
                        available_participants.append(participant)
            
            if not available_participants:
                break
                
            # Generate dialogue turn
            dialogue_turn = self._generate_dialogue_turn(topic, dialogue_history, available_participants)
            dialogue_history.append(dialogue_turn)
            
            # Add to conversation memory
            self.conversation_memory.add_dialogue_turn(self.name, topic, dialogue_turn)
            
        return dialogue_history
    
    def _should_join_dialogue(self, other_agent):
        """Determine if agent should join a dialogue based on persona and schedule"""
        # Simple implementation - can be enhanced based on persona
        return True
    
    def _generate_dialogue_turn(self, topic: str, history: List[Dict], participants: List[str]):
        """Generate a dialogue turn"""
        system_prompt = f"""
        你是{self.name}，人设：{self.persona}。
        你的对话风格：{self.dialogue_style}。
        当前话题：{topic}
        对话历史：{history}
        参与者：{participants}
        
        请生成你的一句话回应，保持符合你的角色设定。
        """
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            return {
                "speaker": self.name,
                "message": response.content,
                "timestamp": str(datetime.now())
            }
        except Exception as e:
            return {
                "speaker": self.name,
                "message": f"无法生成回应: {e}",
                "timestamp": str(datetime.now())
            }
    
    def participate_in_dialogue(self, topic: str, history: List[Dict], participants: List[str], max_rounds: int):
        """Participate in an ongoing dialogue"""
        if not self._should_join_dialogue(self):
            return None
            
        return self._generate_dialogue_turn(topic, history, participants)
    
    def start_battle(self, opponent: str, world_simulator):
        """Initiate a battle with another agent"""
        # Simulate battle
        battle_result = self._simulate_battle(opponent)
        
        # Create long-term memory of the battle
        battle_memory = {
            "id": str(uuid.uuid4()),
            "type": "battle",
            "timestamp": str(datetime.now()),
            "participants": [self.name, opponent],
            "result": battle_result,
            "summary": f"与{opponent}的战斗结果：{battle_result}"
        }
        
        self.long_term_memory.add_memory(battle_memory)
        
        return battle_result
    
    def _simulate_battle(self, opponent: str):
        """Simulate a battle and return result"""
        # Simple simulation - can be enhanced
        import random
        outcomes = ["胜利", "失败", "平局"]
        return random.choice(outcomes)
    
    def generate_memory(self, event: Dict):
        """Generate a memory from an event"""
        memory_content = f"{self.name}在{event.get('location', '未知地点')}进行了{event.get('activity', '未知活动')}，结果是{event.get('result', '未记录')}"
        
        memory = {
            "id": str(uuid.uuid4()),
            "type": event.get("type", "general"),
            "timestamp": str(datetime.now()),
            "content": memory_content,
            "event": event,
            "weight": 1.0
        }
        
        self.long_term_memory.add_memory(memory)
        return memory
    
    def get_action_for_time_slot(self, time_slot: str):
        """Get the action for a specific time slot from current schedule"""
        return self.current_schedule.get(time_slot, {
            "activity": "自由活动", 
            "location": self.current_location or "未知地点", 
            "reason": "未安排"
        })