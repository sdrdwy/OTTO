"""
Exam System for AI Town
Generates exams from knowledge base and evaluates agents' performance
"""
import json
import random
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from memory.knowledge_base import KnowledgeBase


class ExamSystem:
    def __init__(self, knowledge_base_path: str = "memory/expert_knowledge_base.jsonl"):
        self.knowledge_base_path = knowledge_base_path
        self.exam_questions = []
        self.exam_results = {}
        
    def generate_exam(self, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        Generate an exam based on the knowledge base content
        """
        # Load knowledge base from JSONL file
        knowledge_entries = []
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        knowledge_entries.append(json.loads(line))
        except FileNotFoundError:
            print(f"Knowledge base file {self.knowledge_base_path} not found. Using sample questions.")
            # Generate sample questions if knowledge base is not available
            sample_questions = [
                {"question": "What is the derivative of x^2?", "answer": "2x", "category": "Mathematics"},
                {"question": "What is the speed of light?", "answer": "299,792,458 m/s", "category": "Science"},
                {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare", "category": "Literature"},
                {"question": "When did World War II end?", "answer": "1945", "category": "History"}
            ]
            self.exam_questions = random.sample(sample_questions, min(num_questions, len(sample_questions)))
            return self.exam_questions
        
        # Generate questions based on knowledge entries
        questions = []
        for entry in knowledge_entries:
            if "content" in entry:
                content = entry["content"]
                category = entry.get("category", "General")
                
                # Generate a question based on the content
                # This is a simple approach - in a real system, you'd want more sophisticated question generation
                question_text = self._generate_question_from_content(content, category)
                answer = content  # Use the content as the answer (simplified)
                
                questions.append({
                    "question": question_text,
                    "answer": answer,
                    "category": category,
                    "difficulty": "medium"
                })
        
        # Select random questions up to the requested number
        self.exam_questions = random.sample(questions, min(num_questions, len(questions)))
        return self.exam_questions
    
    def _generate_question_from_content(self, content: str, category: str) -> str:
        """
        Generate a question based on the content
        """
        # Simple question generation - in practice, this would be more sophisticated
        if category == "Mathematics":
            return f"Explain the concept of: {content[:50]}..."
        elif category == "Science":
            return f"What is the significance of: {content[:50]}..."
        elif category == "Literature":
            return f"Analyze the meaning of: {content[:50]}..."
        else:
            return f"What is the significance of: {content[:50]}..."
    
    def administer_exam(self, agents: List[BaseAgent]) -> Dict[str, Any]:
        """
        Administer the exam to all agents and return results
        """
        if not self.exam_questions:
            self.generate_exam()
        
        results = {}
        
        for agent in agents:
            print(f"\nAdministering exam to {agent.name}...")
            
            score = 0
            total_questions = len(self.exam_questions)
            
            for i, question in enumerate(self.exam_questions):
                print(f"  Question {i+1}/{total_questions}: {question['question']}")
                
                # Agent attempts to answer the question
                prompt = f"Answer the following question: {question['question']}"
                agent_response = agent.get_response(prompt, f"You are taking an exam. Answer the question as accurately as possible.")
                
                print(f"  {agent.name} response: {agent_response}")
                
                # Simple scoring - in practice, this would be more sophisticated
                # For now, we'll just record the response
                if self._evaluate_answer(agent_response, question['answer']):
                    score += 1
            
            # Calculate final score
            final_score = score / total_questions if total_questions > 0 else 0
            results[agent.name] = {
                "score": final_score,
                "correct_answers": score,
                "total_questions": total_questions,
                "responses": []  # We could store responses if needed
            }
            
            print(f"  {agent.name} final score: {final_score:.2%} ({score}/{total_questions})")
        
        return results
    
    def _evaluate_answer(self, agent_response: str, correct_answer: str) -> bool:
        """
        Simple answer evaluation - in practice, this would use more sophisticated methods
        """
        # Simple similarity check
        agent_response_lower = agent_response.lower()
        correct_answer_lower = correct_answer.lower()
        
        # Check if the correct answer is mentioned in the response
        if correct_answer_lower in agent_response_lower:
            return True
        
        # Additional checks could be implemented here
        return False
    
    def save_exam_results(self, results: Dict[str, Any], filename: str = "exam_results.json"):
        """
        Save exam results to a file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Exam results saved to {filename}")
    
    def compare_results(self, initial_results: Dict[str, Any], final_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare initial and final exam results
        """
        comparison = {}
        
        for agent_name in initial_results:
            if agent_name in final_results:
                initial_score = initial_results[agent_name]["score"]
                final_score = final_results[agent_name]["score"]
                
                comparison[agent_name] = {
                    "initial_score": initial_score,
                    "final_score": final_score,
                    "improvement": final_score - initial_score,
                    "improvement_percentage": ((final_score - initial_score) / initial_score * 100) if initial_score != 0 else 0
                }
        
        return comparison