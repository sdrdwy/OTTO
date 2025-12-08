import json
import os
import time
from typing import List, Dict, Any, Optional


class MemoryManager:
    def __init__(self, memory_file_path: str = "./memory/memory.jsonl", capacity: int = 100):
        self.memory_file_path = memory_file_path
        self.capacity = capacity
        self.memories = self.load_memories()

    def load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from the JSONL file."""
        if not os.path.exists(self.memory_file_path):
            return []
        
        memories = []
        with open(self.memory_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    memories.append(json.loads(line.strip()))
        return memories

    def save_memories(self):
        """Save memories to the JSONL file."""
        with open(self.memory_file_path, 'w', encoding='utf-8') as file:
            for memory in self.memories:
                file.write(json.dumps(memory) + '\n')

    def add_memory(self, agent_name: str, content: str, memory_type: str = "event"):
        """Add a new memory with timestamp and access count."""
        memory = {
            "id": len(self.memories) + 1,
            "agent": agent_name,
            "content": content,
            "type": memory_type,
            "timestamp": time.time(),
            "access_count": 1,
            "weight": 1.0
        }
        
        self.memories.append(memory)
        
        # Maintain memory capacity by removing oldest memories if needed
        if len(self.memories) > self.capacity:
            # Sort by timestamp to remove oldest
            self.memories.sort(key=lambda x: x['timestamp'])
            self.memories = self.memories[-self.capacity:]
        
        self.save_memories()

    def search_memories(self, agent_name: str, query: str = "", memory_type: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories based on agent name, query, and type."""
        results = []
        
        for memory in self.memories:
            # Filter by agent if specified
            if agent_name and memory['agent'] != agent_name:
                continue
                
            # Filter by type if specified
            if memory_type and memory['type'] != memory_type:
                continue
                
            # Filter by query if specified
            if query and query.lower() not in memory['content'].lower():
                continue
                
            results.append(memory)
        
        # Sort by weight and access count (prioritize more relevant memories)
        results.sort(key=lambda x: (x['weight'] * x['access_count']), reverse=True)
        
        return results[:limit]

    def update_memory_weight(self, memory_id: int, new_weight: float):
        """Update the weight of a specific memory."""
        for memory in self.memories:
            if memory['id'] == memory_id:
                memory['weight'] = new_weight
                memory['access_count'] += 1
                break
        self.save_memories()

    def modify_memory(self, memory_id: int, new_content: str):
        """Modify the content of an existing memory."""
        for memory in self.memories:
            if memory['id'] == memory_id:
                memory['content'] = new_content
                memory['access_count'] += 1
                break
        self.save_memories()

    def get_recent_memories(self, agent_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent memories for an agent."""
        agent_memories = [m for m in self.memories if m['agent'] == agent_name]
        agent_memories.sort(key=lambda x: x['timestamp'], reverse=True)
        return agent_memories[:limit]