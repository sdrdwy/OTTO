import json
import jsonlines
from typing import List, Dict, Any, Optional
import os


class KnowledgeManager:
    def __init__(self, knowledge_file_path: str = "/workspace/ai_town/knowledge_base/math_knowledge.jsonl"):
        self.knowledge_file_path = knowledge_file_path
        self.knowledge_base = self.load_knowledge_base()
    
    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Load knowledge base from JSONL file
        """
        knowledge_list = []
        
        if not os.path.exists(self.knowledge_file_path):
            print(f"Knowledge base file not found: {self.knowledge_file_path}")
            return knowledge_list
        
        with jsonlines.open(self.knowledge_file_path) as reader:
            for item in reader:
                knowledge_list.append(item)
        
        return knowledge_list
    
    def retrieve_all_knowledge(self) -> List[Dict[str, Any]]:
        """
        Retrieve all knowledge segments
        """
        return self.knowledge_base
    
    def search_knowledge(self, query: str, subject: Optional[str] = None, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base based on query, subject, or topic
        """
        results = []
        
        for item in self.knowledge_base:
            # Check if item matches search criteria
            matches = True
            
            if query and query.lower() not in item.get('content', '').lower():
                matches = False
            
            if subject and subject.lower() not in item.get('subject', '').lower():
                matches = False
                
            if topic and topic.lower() not in item.get('topic', '').lower():
                matches = False
            
            if matches:
                results.append(item)
        
        return results
    
    def get_topics_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """
        Get all topics for a specific subject
        """
        return [item for item in self.knowledge_base if item.get('subject', '').lower() == subject.lower()]
    
    def get_knowledge_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Get knowledge segments by difficulty level
        """
        return [item for item in self.knowledge_base if item.get('difficulty', '').lower() == difficulty.lower()]