import json
import jsonlines
from datetime import datetime
from typing import Dict, List, Any, Optional
import os


class MemoryManager:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.short_term_memory_file = f"/workspace/ai_town/memory/{agent_name}_short_term.jsonl"
        self.long_term_memory_file = f"/workspace/ai_town/memory/{agent_name}_long_term.jsonl"
        
        # Initialize memory files if they don't exist
        self._init_memory_files()
    
    def _init_memory_files(self):
        """
        Initialize memory files if they don't exist
        """
        for file_path in [self.short_term_memory_file, self.long_term_memory_file]:
            if not os.path.exists(file_path):
                # Create empty file
                with open(file_path, 'w') as f:
                    pass  # Create empty file
    
    def add_memory(self, memory: Dict[str, Any], long_term: bool = False):
        """
        Add a memory entry to either short-term or long-term memory
        """
        file_path = self.long_term_memory_file if long_term else self.short_term_memory_file
        
        # Add timestamp if not present
        if 'timestamp' not in memory:
            memory['timestamp'] = datetime.now().isoformat()
        
        # Add access count for long-term memories
        if long_term:
            memory['access_count'] = memory.get('access_count', 0) + 1
            memory['weight'] = memory.get('weight', 1.0)  # Initial weight
        
        # Write to JSONL file
        with jsonlines.open(file_path, mode='a') as writer:
            writer.write(memory)
    
    def search_memories(self, query: Optional[str] = None, memory_type: Optional[str] = None, 
                       limit: int = 10, long_term: bool = False) -> List[Dict[str, Any]]:
        """
        Search memories based on query, type, or other criteria
        """
        file_path = self.long_term_memory_file if long_term else self.short_term_memory_file
        
        if not os.path.exists(file_path):
            return []
        
        memories = []
        
        with jsonlines.open(file_path) as reader:
            for item in reader:
                # Apply filters
                match = True
                
                if query and query.lower() not in json.dumps(item).lower():
                    match = False
                
                if memory_type and item.get('type') != memory_type:
                    match = False
                
                if match:
                    memories.append(item)
        
        # Sort by timestamp (most recent first) for short-term, by weight/access count for long-term
        if long_term:
            memories.sort(key=lambda x: x.get('weight', 1) * x.get('access_count', 1), reverse=True)
        else:
            memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return memories[:limit]
    
    def update_memory_weight(self, memory_id: str, new_weight: float, long_term: bool = True):
        """
        Update the weight of a specific memory in long-term storage
        """
        if not long_term:
            return  # Only update weights for long-term memories
        
        file_path = self.long_term_memory_file
        
        if not os.path.exists(file_path):
            return
        
        # Read all memories
        all_memories = []
        with jsonlines.open(file_path) as reader:
            for item in reader:
                all_memories.append(item)
        
        # Update the specific memory
        updated = False
        for memory in all_memories:
            # For now, we'll match by timestamp as an ID proxy
            # In a more sophisticated system, we'd have a proper ID
            if memory.get('timestamp') == memory_id:
                memory['weight'] = new_weight
                updated = True
                break
        
        if updated:
            # Rewrite the entire file with updated memories
            with open(file_path, 'w') as f:
                pass  # Clear the file
            
            with jsonlines.open(file_path, mode='a') as writer:
                for memory in all_memories:
                    writer.write(memory)
    
    def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent memories
        """
        return self.search_memories(limit=limit, long_term=False)
    
    def get_important_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most important long-term memories based on weight and access count
        """
        return self.search_memories(limit=limit, long_term=True)