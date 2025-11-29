"""
Knowledge Base System for AI Town
Manages knowledge for expert agents (with content) and student agents (initially empty)
"""
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime


class KnowledgeBase:
    def __init__(self, kb_file: str = None, is_empty: bool = False):
        self.kb_file = kb_file or "knowledge_base.json"
        self.is_empty = is_empty
        self.knowledge_entries: Dict[str, List[Dict]] = {}
        
        if not self.is_empty and os.path.exists(self.kb_file):
            try:
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    self.knowledge_entries = json.load(f)
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
                self.knowledge_entries = {}
        elif self.is_empty:
            # Initialize with empty knowledge for student agents
            self.knowledge_entries = {}
    
    def save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            with open(self.kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_entries, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def add_knowledge(self, category: str, content: str, source: str = "user", metadata: Dict = None):
        """Add knowledge to the knowledge base"""
        if metadata is None:
            metadata = {}
        
        timestamp = datetime.now().isoformat()
        
        if category not in self.knowledge_entries:
            self.knowledge_entries[category] = []
        
        knowledge_entry = {
            "content": content,
            "source": source,
            "timestamp": timestamp,
            "metadata": metadata
        }
        
        self.knowledge_entries[category].append(knowledge_entry)
        self.save_knowledge_base()
    
    def get_knowledge(self, category: str, limit: int = 10) -> List[Dict]:
        """Get knowledge entries from a specific category"""
        if category not in self.knowledge_entries:
            return []
        
        # Return the most recent entries
        return self.knowledge_entries[category][-limit:]
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """Search for knowledge entries containing the query"""
        results = []
        
        categories_to_search = [category] if category else self.knowledge_entries.keys()
        
        for cat in categories_to_search:
            if cat in self.knowledge_entries:
                for entry in self.knowledge_entries[cat]:
                    if query.lower() in entry["content"].lower():
                        entry_copy = entry.copy()
                        entry_copy["category"] = cat
                        results.append(entry_copy)
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all knowledge categories"""
        return list(self.knowledge_entries.keys())
    
    def get_knowledge_summary(self) -> str:
        """Get a summary of the knowledge base"""
        if self.is_empty:
            return "This is an empty knowledge base for student agents."
        
        summary = "Knowledge Base Summary:\n"
        for category, entries in self.knowledge_entries.items():
            summary += f"- {category}: {len(entries)} entries\n"
        
        return summary


class AgentKnowledgeManager:
    def __init__(self, agent_type: str = "student"):
        self.agent_type = agent_type
        
        if agent_type == "expert":
            # Expert agents get a knowledge base with content
            self.knowledge_base = KnowledgeBase("expert_knowledge_base.json", is_empty=False)
            self._initialize_expert_knowledge()
        else:
            # Student agents get an empty knowledge base
            self.knowledge_base = KnowledgeBase(f"student_{int(datetime.now().timestamp())}_knowledge_base.json", is_empty=True)
    
    def _initialize_expert_knowledge(self):
        """Initialize expert knowledge base with sample content"""
        sample_knowledge = {
            "Mathematics": [
                "Algebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols.",
                "Calculus is the mathematical study of continuous change.",
                "Geometry is concerned with the properties of space that are related with distance, shape, size, and relative position of figures."
            ],
            "Science": [
                "The scientific method is an empirical method of acquiring knowledge that has characterized the development of science since at least the 17th century.",
                "Physics is the natural science that studies matter, its motion and behavior through space and time, and the related entities of energy and force.",
                "Chemistry is the scientific study of the properties and behavior of matter."
            ],
            "Literature": [
                "Literature is a form of art that uses language to express ideas, emotions, and stories.",
                "Classic literature includes works that are considered to have lasting artistic merit."
            ],
            "History": [
                "History is the study of the past, particularly how it relates to humans.",
                "Ancient civilizations include Mesopotamia, Egypt, Greece, and Rome."
            ]
        }
        
        for category, entries in sample_knowledge.items():
            for entry in entries:
                self.knowledge_base.add_knowledge(category, entry, source="initialization")
    
    def add_knowledge_from_interaction(self, category: str, content: str, source_agent: str):
        """Add knowledge gained from interactions"""
        if self.agent_type == "expert":
            self.knowledge_base.add_knowledge(category, content, source_agent)
    
    def get_relevant_knowledge(self, category: str, query: str = None) -> List[Dict]:
        """Get relevant knowledge for the agent"""
        if query:
            return self.knowledge_base.search_knowledge(query, category)
        else:
            return self.knowledge_base.get_knowledge(category)
    
    def update_knowledge_from_memory(self, memory_content: str, category_hint: str = None):
        """Update knowledge base based on memory content"""
        if self.agent_type == "expert":
            # Experts can add to their knowledge
            category = category_hint or "General"
            self.knowledge_base.add_knowledge(category, memory_content, "memory_integration")
        # Students keep their knowledge base empty by design, but could potentially learn over time
        # For now, we'll allow students to also add to their knowledge base as they learn
        else:
            category = category_hint or "Learning"
            self.knowledge_base.add_knowledge(category, memory_content, "learning_experience")