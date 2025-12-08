from typing import Dict, List, Any
from .base_agent import BaseAgent


class StudentAgent(BaseAgent):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.learning_goals = self.config.get('goals', [])
        self.learning_style = self.config.get('learning_style', 'general')

    def ask_question(self, expert_agent: 'ExpertAgent', question: str) -> str:
        """Ask a question to an expert agent"""
        answer = expert_agent.answer_question(self, question)
        
        # Add the question and answer to memory
        self.add_memory(
            f"Asked {expert_agent.name}: {question}. Answer: {answer[:100]}...", 
            importance=0.8, 
            metadata={"type": "question_to_expert", "expert": expert_agent.name, "question": question}
        )
        
        return answer

    def study_topic(self, topic: str, duration: str = "session"):
        """Study a specific topic"""
        study_memory = f"Studied {topic} for {duration}"
        self.add_memory(study_memory, importance=0.7, metadata={"activity": "studying", "topic": topic})
        
        return f"{self.name} studied {topic}"

    def take_exam(self, exam_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Take an exam and return results"""
        results = {
            "student": self.name,
            "exam_score": 0,
            "answers": [],
            "grade": "F"
        }
        
        correct_answers = 0
        total_questions = len(exam_questions)
        
        for question in exam_questions:
            # Generate answer based on the agent's knowledge (from memories)
            answer = self._generate_answer_for_exam_question(question)
            results["answers"].append({
                "question_id": question["id"],
                "question": question["question"],
                "generated_answer": answer,
                "topic": question.get("topic", "general")
            })
            
            # For simplicity, we're not grading the answers automatically
            # In a real implementation, you would have a more sophisticated grading system
            correct_answers += 1  # Assume all answers are correct for now
        
        # Calculate score
        if total_questions > 0:
            score_percentage = (correct_answers / total_questions) * 100
            results["exam_score"] = round(score_percentage, 2)
            
            # Assign grade based on score
            if score_percentage >= 90:
                results["grade"] = "A"
            elif score_percentage >= 80:
                results["grade"] = "B"
            elif score_percentage >= 70:
                results["grade"] = "C"
            elif score_percentage >= 60:
                results["grade"] = "D"
            else:
                results["grade"] = "F"
        
        # Add exam experience to memory
        self.add_memory(
            f"Took exam with {total_questions} questions, scored {results['exam_score']}%", 
            importance=0.9, 
            metadata={"activity": "exam", "score": results['exam_score'], "grade": results['grade']}
        )
        
        return results

    def _generate_answer_for_exam_question(self, question: Dict[str, Any]) -> str:
        """Generate an answer for an exam question based on agent's knowledge"""
        # Search memories for relevant information to answer the question
        relevant_memories = self.search_memory(question["question"], top_k=3)
        
        # If we have relevant memories, use them to form an answer
        if relevant_memories:
            memory_content = " ".join([mem.content for mem in relevant_memories])
            answer_context = f"Based on my knowledge: {memory_content[:500]}"
        else:
            answer_context = "I don't have specific knowledge about this topic, but I can try to answer based on general understanding."
        
        # Create a prompt to generate an answer using LLM
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"You are {self.name}, a student. Answer the following exam question based on your knowledge and understanding."),
            HumanMessage(content=f"Question: {question['question']}\n\nMy knowledge: {answer_context}\n\nProvide a thoughtful answer to this question.")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return response.content