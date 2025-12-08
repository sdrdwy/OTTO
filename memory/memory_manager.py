import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_file_path: str = "memory/memory.jsonl", capacity: int = 100):
        self.memory_file_path = memory_file_path
        self.capacity = capacity
        self.memories = []
        self.load_memories()
    
    def load_memories(self):
        """Load memories from the JSONL file"""
        if os.path.exists(self.memory_file_path):
            with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        memory = json.loads(line.strip())
                        self.memories.append(memory)
        else:
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            with open(self.memory_file_path, 'w') as f:
                pass  # Create an empty file
    
    def save_memories(self):
        """Save memories to the JSONL file"""
        with open(self.memory_file_path, 'w', encoding='utf-8') as f:
            for memory in self.memories:
                f.write(json.dumps(memory) + '\n')
    
    def add_memory(self, agent_name: str, content: str, memory_type: str = "event", 
                   timestamp: Optional[float] = None, related_agents: List[str] = None):
        """Add a new memory with timestamp and access count"""
        if related_agents is None:
            related_agents = []
        
        if timestamp is None:
            timestamp = time.time()
        
        memory = {
            "id": len(self.memories),
            "agent": agent_name,
            "content": content,
            "type": memory_type,
            "timestamp": timestamp,
            "access_count": 1,
            "related_agents": related_agents,
            "weight": 1.0  # Initial weight
        }
        
        self.memories.append(memory)
        
        # Keep only the most recent memories within capacity
        if len(self.memories) > self.capacity:
            # Sort by access count and recency (higher access count and more recent first)
            self.memories.sort(key=lambda x: (x['access_count'], x['timestamp']), reverse=True)
            self.memories = self.memories[:self.capacity]
        
        self.save_memories()
        return memory["id"]
    
    def search_memories(self, agent_name: str, query: str = "", memory_type: str = "", 
                        time_range: tuple = None, related_agents: List[str] = None, 
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories based on various criteria"""
        if related_agents is None:
            related_agents = []
        
        results = []
        
        for memory in self.memories:
            # Filter by agent if specified
            if agent_name and memory["agent"] != agent_name:
                continue
            
            # Filter by query in content
            if query and query.lower() not in memory["content"].lower():
                continue
            
            # Filter by memory type
            if memory_type and memory["type"] != memory_type:
                continue
            
            # Filter by time range
            if time_range:
                start_time, end_time = time_range
                if memory["timestamp"] < start_time or memory["timestamp"] > end_time:
                    continue
            
            # Filter by related agents
            if related_agents:
                if not any(agent in memory["related_agents"] for agent in related_agents):
                    continue
            
            # Update access count and weight
            memory["access_count"] += 1
            # Increase weight based on access frequency
            memory["weight"] = min(10.0, memory["weight"] + 0.1)
            
            results.append(memory)
        
        # Sort by weight (access frequency) and recency
        results.sort(key=lambda x: (x['weight'], x['timestamp']), reverse=True)
        
        return results[:limit]
    
    def update_memory(self, memory_id: int, new_content: str = None, 
                      new_type: str = None, new_related_agents: List[str] = None):
        """Update an existing memory"""
        for memory in self.memories:
            if memory["id"] == memory_id:
                if new_content is not None:
                    memory["content"] = new_content
                if new_type is not None:
                    memory["type"] = new_type
                if new_related_agents is not None:
                    memory["related_agents"] = new_related_agents
                self.save_memories()
                return True
        return False

    def get_agent_memories(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all memories for a specific agent"""
        return [mem for mem in self.memories if mem["agent"] == agent_name]
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories across all agents"""
        sorted_memories = sorted(self.memories, key=lambda x: x["timestamp"], reverse=True)
        return sorted_memories[:limit]