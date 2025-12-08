from typing import Dict, List, Any
from .agent import Agent


class StudentAgent(Agent):
    def __init__(self, config_file: str):
        super().__init__(config_file)
        # Students don't have access to knowledge base directly, but they learn through interactions
        self.learned_topics = []
        self.study_progress = {}
    
    def attend_class(self, teacher_name: str, lesson_content: str) -> str:
        """
        Attend a class and learn from the teacher
        """
        learning_prompt = f"""
        As {self.name}, a {self.role}, listen to this lesson from {teacher_name}:
        
        LESSON CONTENT:
        {lesson_content}
        
        PERSONA:
        - Personality: {self.personality}
        
        How do you react to this lesson? What do you understand? What questions do you have?
        """
        
        try:
            response = self.llm.invoke(learning_prompt)
            
            # Record learning in memory
            self.memory_manager.add_memory({
                "type": "class_attendance",
                "timestamp": "current_time",
                "teacher": teacher_name,
                "lesson_content": lesson_content,
                "student_response": response.content,
                "understanding_level": "medium"  # Would be determined by analysis in real implementation
            })
            
            # Update learned topics
            self.learned_topics.append({
                "topic": lesson_content[:50] + "...",  # Brief description
                "learned_on": "current_day",
                "understanding": response.content
            })
            
            return response.content
        except Exception as e:
            print(f"Error during class attendance for {self.name}: {e}")
            return f"{self.name} listened to the class attentively."
    
    def study_independently(self, topic: str) -> str:
        """
        Study a topic independently (based on memories and general knowledge)
        """
        study_prompt = f"""
        As {self.name}, a {self.role}, study the following topic independently:
        
        TOPIC: {topic}
        
        PERSONA:
        - Personality: {self.personality}
        
        What do you know about this topic? How do you approach studying it? What insights do you gain?
        """
        
        try:
            response = self.llm.invoke(study_prompt)
            
            # Record study session in memory
            self.memory_manager.add_memory({
                "type": "independent_study",
                "timestamp": "current_time",
                "topic": topic,
                "study_notes": response.content
            })
            
            return response.content
        except Exception as e:
            print(f"Error during independent study for {self.name}: {e}")
            return f"{self.name} studied the topic of {topic}."
    
    def ask_question(self, to_agent: str, question: str) -> str:
        """
        Ask a question to another agent (teacher or fellow student)
        """
        question_prompt = f"""
        As {self.name}, ask this question to {to_agent}:
        
        QUESTION: {question}
        
        PERSONA:
        - Personality: {self.personality}
        - Dialogue style: {self.dialogue_style}
        
        Formulate your question in a way that fits your personality.
        """
        
        try:
            response = self.llm.invoke(question_prompt)
            
            # Record the question in memory
            self.memory_manager.add_memory({
                "type": "asking_question",
                "timestamp": "current_time",
                "recipient": to_agent,
                "question": question,
                "formulated_question": response.content
            })
            
            return response.content
        except Exception as e:
            print(f"Error asking question for {self.name}: {e}")
            return question
    
    def review_learned_material(self) -> str:
        """
        Review material that has been learned so far
        """
        if not self.learned_topics:
            return "No material to review yet."
        
        review_prompt = f"""
        As {self.name}, review the following topics you've learned:
        
        LEARNED TOPICS:
        {chr(10).join([f"- {topic['topic']} on {topic['learned_on']}" for topic in self.learned_topics[-5:]])}  # Last 5 topics
        
        PERSONA:
        - Personality: {self.personality}
        
        Reflect on what you've learned. What connections do you see? What do you want to explore further?
        """
        
        try:
            response = self.llm.invoke(review_prompt)
            
            # Record review session in memory
            self.memory_manager.add_memory({
                "type": "material_review",
                "timestamp": "current_time",
                "review_content": response.content,
                "topics_reviewed": [t['topic'] for t in self.learned_topics[-5:]]
            })
            
            return response.content
        except Exception as e:
            print(f"Error during material review for {self.name}: {e}")
            return f"{self.name} reviewed the learned material."