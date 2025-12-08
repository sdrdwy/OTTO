import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class LongTermMemory:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.memory_file = f"memory/long_term_memories_{agent_name}.jsonl"
        self.memories = []
        self.load_memories()
    
    def add_memory(self, content: str, memory_type: str, metadata: Dict[str, Any] = None) -> str:
        """Add a memory with content, type, and metadata"""
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "access_count": 1,
            "weight": 1.0  # Initial weight
        }
        
        # Add to in-memory list
        self.memories.append(memory)
        
        # Save to file
        self._save_memory_to_file(memory)
        
        return memory_id
    
    def _save_memory_to_file(self, memory: Dict) -> None:
        """Save a single memory to the JSONL file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(memory, ensure_ascii=False) + '\n')
    
    def load_memories(self) -> None:
        """Load memories from the JSONL file"""
        if not os.path.exists(self.memory_file):
            return
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    memory = json.loads(line)
                    self.memories.append(memory)
    
    def search_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search memories based on query with relevance scoring"""
        # Simple keyword-based search for now
        results = []
        query_lower = query.lower()
        
        for memory in self.memories:
            content_lower = memory['content'].lower()
            score = 0
            
            # Calculate relevance score based on keyword matches
            if query_lower in content_lower:
                score += 2
                # Additional points for exact matches at the beginning
                if content_lower.startswith(query_lower):
                    score += 1
                # Additional points based on frequency of query in content
                score += content_lower.count(query_lower)
            
            # Consider metadata in search
            for key, value in memory.get('metadata', {}).items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 1
            
            if score > 0:
                # Adjust score by access count and weight
                adjusted_score = score * memory.get('weight', 1.0)
                results.append((memory, adjusted_score))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return [result[0] for result in results[:top_k]]
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get the most recent memories"""
        return self.memories[-limit:] if len(self.memories) >= limit else self.memories
    
    def update_memory_weight(self, memory_id: str, new_weight: float) -> bool:
        """Update the weight of a specific memory"""
        for i, memory in enumerate(self.memories):
            if memory['id'] == memory_id:
                self.memories[i]['weight'] = new_weight
                self.memories[i]['access_count'] = self.memories[i].get('access_count', 0) + 1
                
                # Save the updated memory back to file
                # This is a simplified approach - in a full implementation we might want to rewrite the entire file
                return True
        return False
    
    def get_memories_by_type(self, memory_type: str) -> List[Dict]:
        """Get all memories of a specific type"""
        return [memory for memory in self.memories if memory.get('type') == memory_type]
    
    def get_all_memories(self) -> List[Dict]:
        """Get all memories"""
        return self.memories