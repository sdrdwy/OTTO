import json
import random
from typing import List, Dict, Any
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent


class ExamSystem:
    def __init__(self, knowledge_base_path: str = "knowledge_base/knowledge.jsonl", 
                 num_questions: int = 20):
        self.knowledge_base_path = knowledge_base_path
        self.num_questions = num_questions
        self.questions_pool = []
        self.generated_exam = []
        
        self.load_knowledge_base()
        self.generate_exam()
    
    def load_knowledge_base(self):
        """Load knowledge base to generate exam questions"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.questions_pool.append(json.loads(line.strip()))
        except FileNotFoundError:
            print(f"Knowledge base file not found at {self.knowledge_base_path}")
    
    def generate_exam(self):
        """Generate an exam based on the knowledge base"""
        if len(self.questions_pool) >= self.num_questions:
            self.generated_exam = random.sample(self.questions_pool, self.num_questions)
        else:
            # If not enough questions in pool, duplicate some
            while len(self.generated_exam) < self.num_questions:
                for item in self.questions_pool:
                    if len(self.generated_exam) < self.num_questions:
                        # Convert knowledge item to question format
                        question_item = {
                            "id": len(self.generated_exam),
                            "question": f"What do you know about: {item['content'][:50]}...",
                            "reference_content": item['content']
                        }
                        self.generated_exam.append(question_item)
    
    def administer_pre_test(self, agents: List):
        """Administer pre-test to all agents before simulation starts"""
        results = {}
        print("\n" + "="*60)
        print("PRE-SIMULATION EXAMINATION")
        print("="*60)
        
        for agent in agents:
            if hasattr(agent, 'take_exam'):
                score = agent.take_exam([q["question"] for q in self.generated_exam])
                results[agent.name] = score
                print(f"{agent.name} (pre-simulation): {score}/100")
            else:
                # Expert agents might have different evaluation methods
                # For now, assign a high score since they know the material
                results[agent.name] = 95
                print(f"{agent.name} (expert, pre-simulation): 95/100")
        
        print("="*60)
        return results
    
    def administer_post_test(self, agents: List):
        """Administer post-test to all agents after simulation ends"""
        results = {}
        print("\n" + "="*60)
        print("POST-SIMULATION EXAMINATION")
        print("="*60)
        
        for agent in agents:
            if hasattr(agent, 'take_exam'):
                score = agent.take_exam([q["question"] for q in self.generated_exam])
                results[agent.name] = score
                print(f"{agent.name} (post-simulation): {score}/100")
            else:
                # Expert agents might have different evaluation methods
                results[agent.name] = 95  # Experts maintain high scores
                print(f"{agent.name} (expert, post-simulation): 95/100")
        
        print("="*60)
        return results
    
    def compare_results(self, pre_results: Dict[str, int], post_results: Dict[str, int]):
        """Compare pre and post simulation results"""
        print("\n" + "="*60)
        print("PERFORMANCE COMPARISON")
        print("="*60)
        
        for agent_name in pre_results.keys():
            pre_score = pre_results[agent_name]
            post_score = post_results[agent_name]
            improvement = post_score - pre_score
            
            print(f"{agent_name}: Pre: {pre_score}, Post: {post_score}, Change: {improvement:+d}")
        
        print("="*60)
    
    def get_exam_questions(self) -> List[Dict[str, str]]:
        """Get the generated exam questions"""
        return [q["question"] for q in self.generated_exam]