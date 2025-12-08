import json
import os
from typing import List, Dict, Any
from pathlib import Path


class KnowledgeBase:
    def __init__(self, subject: str = None):
        self.subject = subject
        self.knowledge_items = []
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load knowledge from JSONL files"""
        # Look for knowledge files in the knowledge_base directory
        knowledge_dir = Path("knowledge_base")
        
        if self.subject:
            # Load subject-specific knowledge
            subject_file = knowledge_dir / f"{self.subject.lower()}.jsonl"
            if subject_file.exists():
                self._load_from_file(subject_file)
        else:
            # Load all knowledge files
            for file_path in knowledge_dir.glob("*.jsonl"):
                self._load_from_file(file_path)
    
    def _load_from_file(self, file_path: Path):
        """Load knowledge from a specific JSONL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        self.knowledge_items.append(item)
        except Exception as e:
            print(f"Error loading knowledge from {file_path}: {e}")
    
    def search(self, query: str) -> List[Dict]:
        """Search for knowledge items related to the query"""
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_items:
            content_lower = item.get('content', '').lower()
            category = item.get('category', '').lower()
            item_id = item.get('id', '')
            
            score = 0
            # Score based on content match
            if query_lower in content_lower:
                score += 2
                score += content_lower.count(query_lower)  # More occurrences = higher score
            
            # Score based on category match
            if query_lower in category:
                score += 1
            
            # Score based on ID match
            if query_lower in item_id.lower():
                score += 1
            
            if score > 0:
                results.append((item, score))
        
        # Sort by score and return items
        results.sort(key=lambda x: x[1], reverse=True)
        return [result[0] for result in results]
    
    def get_topics(self) -> List[str]:
        """Get all unique topics/categories in the knowledge base"""
        categories = set()
        for item in self.knowledge_items:
            category = item.get('category')
            if category:
                categories.add(category)
        return list(categories)
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get knowledge items by category"""
        return [item for item in self.knowledge_items 
                if item.get('category', '').lower() == category.lower()]
    
    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get knowledge items by difficulty level"""
        return [item for item in self.knowledge_items 
                if item.get('difficulty', '').lower() == difficulty.lower()]
    
    def add_knowledge(self, content: str, category: str, difficulty: str = "intermediate"):
        """Add new knowledge item to the base"""
        new_item = {
            "id": f"kb_{len(self.knowledge_items) + 1}",
            "content": content,
            "category": category,
            "difficulty": difficulty,
            "timestamp": "2024-01-01T00:00:00Z"  # In a real system, use current timestamp
        }
        self.knowledge_items.append(new_item)
    
    def get_all_knowledge(self) -> List[Dict]:
        """Get all knowledge items"""
        return self.knowledge_items