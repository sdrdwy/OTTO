"""
Base Agent Class
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
from langchain_core.messages import HumanMessage, SystemMessage
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from utils.mock_llm import MockChatOpenAI
from utils.qwen_llm import QwenChatModel


class BaseAgent(ABC):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator):
        self.name = name
        self.memory = memory
        self.world = world
        
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
        Get response from the LLM with memory context
        """
        # Retrieve relevant memories
        recent_memories = self.memory.get_recent_memories(self.name, limit=5)
        long_term_memories = self.memory.get_long_term_memories(self.name, limit=10)
        
        # Construct the full prompt with context
        context = f"Agent Context: {agent_context}\n" if agent_context else ""
        recent_memory_context = "\n".join([f"- {memory}" for memory in recent_memories])
        long_term_memory_context = "\n".join([f"- (Long-term) {memory}" for memory in long_term_memories])
        
        full_prompt = f"""
        {context}
        Recent memories: {recent_memory_context or 'No recent memories'}
        
        Long-term memories: {long_term_memory_context or 'No long-term memories'}
        
        Current conversation: {prompt}
        
        As {self.name}, respond to the above conversation.
        """
        
        messages = [
            SystemMessage(content=f"You are {self.name}, an AI agent in a simulated world with access to your memories."),
            HumanMessage(content=full_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def remember(self, event: str, memory_type: str = "conversation"):
        """
        Add an event to memory
        """
        self.memory.add_memory(self.name, event, memory_type)
    
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
    
    @abstractmethod
    def interact(self, other_agents: List['BaseAgent'], topic: str = None):
        pass