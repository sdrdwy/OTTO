import json
import random
from typing import Dict, List, Any
from memory.memory_manager import MemoryManager
from agents.agent_base import BaseAgent


class ExpertAgent(BaseAgent):
    def __init__(self, config_path: str, memory_manager: MemoryManager, world_manager, 
                 knowledge_base_path: str = "knowledge_base/knowledge.jsonl"):
        super().__init__(config_path, memory_manager, world_manager)
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = []
        self.curriculum = {}
        
        self.load_knowledge_base()
        self.generate_curriculum()
    
    def load_knowledge_base(self):
        """Load knowledge base from JSONL file"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.knowledge_base.append(json.loads(line.strip()))
        except FileNotFoundError:
            print(f"Knowledge base file not found at {self.knowledge_base_path}")
    
    def generate_curriculum(self, total_days: int = 5):
        """Generate a curriculum based on knowledge base and total simulation days"""
        # Group knowledge by category
        categories = {}
        for item in self.knowledge_base:
            category = item.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Distribute categories across days
        self.curriculum = {}
        categories_list = list(categories.keys())
        
        for day in range(1, total_days + 1):
            self.curriculum[f"day_{day}"] = {
                "topics": [],
                "teaching_points": []
            }
            
            # Assign topics for this day
            topics_for_day = []
            # Cycle through categories to ensure variety
            category_idx = (day - 1) % len(categories_list)
            selected_category = categories_list[category_idx]
            
            # Select a few items from the selected category
            category_items = categories[selected_category]
            selected_items = random.sample(category_items, min(3, len(category_items)))
            
            for item in selected_items:
                topics_for_day.append(item["content"])
                self.curriculum[f"day_{day}"]["teaching_points"].append(item["content"])
            
            self.curriculum[f"day_{day}"]["topics"] = topics_for_day
    
    def get_curriculum_for_day(self, day: int) -> Dict[str, Any]:
        """Get curriculum for a specific day"""
        return self.curriculum.get(f"day_{day}", {"topics": [], "teaching_points": []})
    
    def teach(self, student_names: List[str], topic: str) -> str:
        """Conduct a teaching session"""
        # Find relevant knowledge in the knowledge base
        relevant_knowledge = [item for item in self.knowledge_base 
                              if topic.lower() in item["content"].lower()]
        
        if not relevant_knowledge:
            relevant_knowledge = self.knowledge_base  # Fallback to any knowledge
        
        # Select a random piece of knowledge to teach
        selected_knowledge = random.choice(relevant_knowledge)
        
        teaching_content = f"Today's lesson: {selected_knowledge['content']}"
        
        # Generate memory for the teacher
        self.generate_memory_from_event(
            f"Taught {', '.join(student_names)} about {topic}: {selected_knowledge['content']}", 
            "teaching"
        )
        
        # Also generate memories for students (in a real system, students would have their own memory generation)
        for student_name in student_names:
            # In a real system, each student would generate their own memory
            pass
        
        return teaching_content
    
    def answer_question(self, question: str) -> str:
        """Answer a question using the knowledge base"""
        # Find relevant knowledge
        relevant_knowledge = [item for item in self.knowledge_base 
                              if any(keyword.lower() in item["content"].lower() 
                                    for keyword in question.lower().split())]
        
        if relevant_knowledge:
            # Return the most relevant piece of knowledge
            selected = random.choice(relevant_knowledge)
            answer = f"Based on my knowledge: {selected['content']}"
        else:
            answer = "I don't have specific knowledge about that topic, but I can discuss related concepts."
        
        # Generate memory of the question and answer
        self.generate_memory_from_event(
            f"Answered question '{question}' with '{answer}'", 
            "question_answering"
        )
        
        return answer
    
    def assess_student(self, student_name: str, topic: str) -> int:
        """Assess a student's understanding of a topic"""
        # Generate a simple assessment score based on knowledge
        score = random.randint(60, 100)  # Random score for simulation
        
        assessment_result = f"Assessed {student_name} on {topic}, score: {score}/100"
        
        # Generate memory of the assessment
        self.generate_memory_from_event(assessment_result, "assessment")
        
        return score