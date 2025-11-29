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


class BaseAgent(ABC):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator):
        self.name = name
        self.memory = memory
        self.world = world
        
        # Check if we have an API key, otherwise use mock
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
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
        
        # Construct the full prompt with context
        context = f"Agent Context: {agent_context}\n" if agent_context else ""
        memory_context = "\n".join([f"- {memory}" for memory in recent_memories])
        
        full_prompt = f"""
        {context}
        Relevant memories: {memory_context or 'No recent memories'}
        
        Current conversation: {prompt}
        
        As {self.name}, respond to the above conversation.
        """
        
        messages = [
            SystemMessage(content=f"You are {self.name}, an AI agent in a simulated world."),
            HumanMessage(content=full_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def remember(self, event: str):
        """
        Add an event to memory
        """
        self.memory.add_memory(self.name, event)
    
    @abstractmethod
    def interact(self, other_agents: List['BaseAgent'], topic: str = None):
        pass