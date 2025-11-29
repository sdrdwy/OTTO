"""
Conversation Memory System
Stores and retrieves memories for agents
"""
from typing import List, Dict
from datetime import datetime
import json


class ConversationMemory:
    def __init__(self, max_memories_per_agent: int = 50):
        self.memories: Dict[str, List[Dict]] = {}
        self.max_memories_per_agent = max_memories_per_agent
        
    def add_memory(self, agent_name: str, content: str):
        """
        Add a memory for a specific agent
        """
        timestamp = datetime.now().isoformat()
        
        if agent_name not in self.memories:
            self.memories[agent_name] = []
        
        # Create memory entry
        memory_entry = {
            "timestamp": timestamp,
            "content": content
        }
        
        # Add to the beginning of the list (most recent first)
        self.memories[agent_name].insert(0, memory_entry)
        
        # Keep only the most recent memories (up to max_memories_per_agent)
        if len(self.memories[agent_name]) > self.max_memories_per_agent:
            self.memories[agent_name] = self.memories[agent_name][:self.max_memories_per_agent]
    
    def get_recent_memories(self, agent_name: str, limit: int = 10) -> List[str]:
        """
        Get recent memories for a specific agent
        """
        if agent_name not in self.memories:
            return []
        
        recent_memories = self.memories[agent_name][:limit]
        return [memory["content"] for memory in recent_memories]
    
    def get_all_memories(self, agent_name: str) -> List[Dict]:
        """
        Get all memories for a specific agent
        """
        return self.memories.get(agent_name, [])
    
    def search_memories(self, agent_name: str, query: str) -> List[Dict]:
        """
        Search for specific memories containing the query
        """
        if agent_name not in self.memories:
            return []
        
        matching_memories = []
        for memory in self.memories[agent_name]:
            if query.lower() in memory["content"].lower():
                matching_memories.append(memory)
        
        return matching_memories
    
    def clear_agent_memories(self, agent_name: str):
        """
        Clear all memories for a specific agent
        """
        if agent_name in self.memories:
            del self.memories[agent_name]
    
    def get_memory_summary(self) -> str:
        """
        Get a summary of all memories
        """
        summary = "Memory Summary:\n"
        for agent_name, agent_memories in self.memories.items():
            summary += f"- {agent_name}: {len(agent_memories)} memories\n"
        return summary