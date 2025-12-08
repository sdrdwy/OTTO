from typing import List, Dict, Any
from memory.memory_manager import MemoryManager
from agents.agent_base import BaseAgent


class StudentAgent(BaseAgent):
    def __init__(self, config_path: str, memory_manager: MemoryManager, world_manager):
        super().__init__(config_path, memory_manager, world_manager)
        self.learning_progress = {}
        self.exam_scores = []
    
    def study_topic(self, topic: str) -> str:
        """Study a specific topic and generate memory"""
        study_result = f"Studied {topic} based on personal notes and understanding"
        
        # Generate memory of studying
        self.generate_memory_from_event(f"Studied topic: {topic}", "study_session")
        
        # Update learning progress
        if topic not in self.learning_progress:
            self.learning_progress[topic] = 0
        self.learning_progress[topic] += 1
        
        return study_result
    
    def ask_question(self, teacher: 'ExpertAgent', question: str) -> str:
        """Ask a question to the teacher"""
        # Generate memory of asking question
        self.generate_memory_from_event(f"Asked teacher: {question}", "question_asked")
        
        # Get answer from teacher
        answer = teacher.answer_question(question)
        
        # Generate memory of receiving answer
        self.generate_memory_from_event(f"Received answer to question '{question}': {answer}", "learning")
        
        return answer
    
    def take_exam(self, exam_questions: List[str]) -> int:
        """Take an exam and return score"""
        score = 0
        total_questions = len(exam_questions)
        
        for question in exam_questions:
            # Simulate answering based on learning progress and memories
            # Students with better learning progress and more relevant memories score higher
            relevant_memories = self.recall_memories(query=question, limit=3)
            if len(relevant_memories) > 0:
                # Higher chance of answering correctly if relevant memories exist
                if len(relevant_memories) > 1:
                    score += 1  # Answer correctly if multiple relevant memories
                else:
                    score += 1 if __import__('random').random() > 0.3 else 0  # 70% chance
            else:
                score += 1 if __import__('random').random() > 0.7 else 0  # 30% chance without relevant memories
        
        exam_score = int((score / total_questions) * 100) if total_questions > 0 else 0
        self.exam_scores.append(exam_score)
        
        # Generate memory of exam
        self.generate_memory_from_event(f"Took exam with {total_questions} questions, scored {exam_score}/100", "exam")
        
        return exam_score
    
    def collaborate_with_classmates(self, classmates: List['StudentAgent'], topic: str) -> str:
        """Collaborate with other students on a topic"""
        collaborators = [self.name] + [classmate.name for classmate in classmates]
        
        collaboration_result = f"Collaborated with {', '.join([c for c in collaborators if c != self.name])} on {topic}"
        
        # Generate memory of collaboration
        self.generate_memory_from_event(collaboration_result, "collaboration")
        
        # Each participating student generates a memory
        for classmate in classmates:
            classmate.generate_memory_from_event(
                f"Collaborated with {', '.join([c for c in collaborators if c != classmate.name])} on {topic}", 
                "collaboration"
            )
        
        return collaboration_result
    
    def get_learning_progress(self) -> Dict[str, int]:
        """Get the student's learning progress"""
        return self.learning_progress.copy()
    
    def get_latest_exam_score(self) -> int:
        """Get the student's latest exam score"""
        return self.exam_scores[-1] if self.exam_scores else 0
    
    def get_overall_performance(self) -> float:
        """Get the student's overall performance based on exam scores"""
        if not self.exam_scores:
            return 0.0
        return sum(self.exam_scores) / len(self.exam_scores)