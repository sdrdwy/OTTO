"""
Conversation Memory System
Stores and retrieves memories for agents with both short-term and long-term storage
"""
from typing import List, Dict
from datetime import datetime
import json
import os


class ConversationMemory:
    def __init__(self, max_memories_per_agent: int = 50, long_term_memory_file: str = "config_files/memory_configs/long_term_memory.json"):
        self.memories: Dict[str, List[Dict]] = {}
        self.max_memories_per_agent = max_memories_per_agent
        self.long_term_memory_file = long_term_memory_file
        self.long_term_memories: Dict[str, List[Dict]] = self.load_long_term_memory()
        
    def load_long_term_memory(self) -> Dict[str, List[Dict]]:
        """Load long-term memory from file if it exists"""
        if os.path.exists(self.long_term_memory_file):
            try:
                with open(self.long_term_memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_long_term_memory(self):
        """Save long-term memory to file"""
        try:
            with open(self.long_term_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving long-term memory: {e}")
    
    def archive_to_long_term(self, agent_name: str, memory_entry: Dict):
        """Move a memory to long-term storage with more detailed content"""
        if agent_name not in self.long_term_memories:
            self.long_term_memories[agent_name] = []
        
        # Enhance the memory entry with more detailed content if it's conversation-related
        enhanced_memory = memory_entry.copy()
        if memory_entry.get("type") == "conversation":
            # Extract and include more detailed content from the conversation
            content = memory_entry.get("content", "")
            details = memory_entry.get("details", {})
            
            # Create more detailed content for long-term storage
            detailed_content = f"Content: {content}"
            if details.get("topic"):
                detailed_content += f" | Topic: {details['topic']}"
            if details.get("participants"):
                detailed_content += f" | Participants: {', '.join(details['participants'])}"
            if details.get("location"):
                detailed_content += f" | Location: {details['location']}"
            if details.get("outcome"):
                detailed_content += f" | Outcome: {details['outcome']}"
            if details.get("context"):
                detailed_content += f" | Context: {details['context'][:200]}..."  # Limit context length
            
            enhanced_memory["detailed_content"] = detailed_content
        
        # Add to the beginning of the list (most recent first)
        self.long_term_memories[agent_name].insert(0, enhanced_memory)
        self.save_long_term_memory()
    
    def add_memory(self, agent_name: str, content: str, memory_type: str = "conversation", **kwargs):
        """
        Add a memory for a specific agent with detailed information
        """
        timestamp = datetime.now().isoformat()
        
        if agent_name not in self.memories:
            self.memories[agent_name] = []
        
        # Create detailed memory entry
        memory_entry = {
            "timestamp": timestamp,
            "content": content,
            "type": memory_type,
            "details": {
                "location": kwargs.get("location", "unknown"),
                "participants": kwargs.get("participants", []),
                "topic": kwargs.get("topic", "general"),
                "context": kwargs.get("context", ""),
                "outcome": kwargs.get("outcome", ""),
                "importance": kwargs.get("importance", "medium"),
                "duration": kwargs.get("duration", ""),
                "related_memories": kwargs.get("related_memories", [])
            }
        }
        
        # Add to the beginning of the list (most recent first)
        self.memories[agent_name].insert(0, memory_entry)
        
        # Keep only the most recent memories (up to max_memories_per_agent)
        if len(self.memories[agent_name]) > self.max_memories_per_agent:
            # Move the oldest memory to long-term storage before removing it
            oldest_memory = self.memories[agent_name].pop()  # Remove oldest (at the end)
            self.archive_to_long_term(agent_name, oldest_memory)
    
    def get_recent_memories(self, agent_name: str, limit: int = 10) -> List[str]:
        """
        Get recent memories for a specific agent
        """
        if agent_name not in self.memories:
            return []
        
        recent_memories = self.memories[agent_name][:limit]
        return [memory["content"] for memory in recent_memories]
    
    def get_long_term_memories(self, agent_name: str, limit: int = 20) -> List[str]:
        """
        Get long-term memories for a specific agent
        """
        if agent_name not in self.long_term_memories:
            return []
        
        recent_long_term = self.long_term_memories[agent_name][:limit]
        # Return detailed content if available, otherwise fall back to original content
        return [memory.get("detailed_content", memory["content"]) for memory in recent_long_term]
    
    def get_all_memories(self, agent_name: str) -> List[Dict]:
        """
        Get all memories (both short and long term) for a specific agent
        """
        short_term = self.memories.get(agent_name, [])
        long_term = self.long_term_memories.get(agent_name, [])
        return short_term + long_term
    
    def search_memories(self, agent_name: str, query: str) -> List[Dict]:
        """
        Search for specific memories containing the query in both short and long term
        """
        results = []
        
        # Search in short-term memories
        if agent_name in self.memories:
            for memory in self.memories[agent_name]:
                if query.lower() in memory["content"].lower():
                    results.append(memory)
        
        # Search in long-term memories
        if agent_name in self.long_term_memories:
            for memory in self.long_term_memories[agent_name]:
                if query.lower() in memory["content"].lower():
                    results.append(memory)
        
        return results
    
    def clear_agent_memories(self, agent_name: str):
        """
        Clear all memories for a specific agent
        """
        if agent_name in self.memories:
            # Archive all short-term memories to long-term before clearing
            for memory in self.memories[agent_name]:
                self.archive_to_long_term(agent_name, memory)
            del self.memories[agent_name]
    
    def get_memory_summary(self) -> str:
        """
        Get a summary of all memories
        """
        summary = "Memory Summary:\n"
        for agent_name, agent_memories in self.memories.items():
            summary += f"- {agent_name}: {len(agent_memories)} short-term memories\n"
        
        for agent_name, agent_long_term_memories in self.long_term_memories.items():
            if agent_name not in self.memories:  # Only add if not already counted above
                summary += f"- {agent_name}: {len(agent_long_term_memories)} long-term memories\n"
            else:
                summary += f"- {agent_name}: {len(agent_long_term_memories)} long-term memories\n"
        return summary