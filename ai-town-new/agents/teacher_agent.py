import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base_agent import BaseAgent
from memory.knowledge_base import KnowledgeBase


class TeacherAgent(BaseAgent):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.teaching_subject = self.config.get('teaching_subject', 'General')
        self.knowledge_base = KnowledgeBase(self.teaching_subject)
        self.teaching_experience = 0
        self.student_interactions = []
        
    def generate_daily_schedule(self, date: str, map_info: Dict, previous_memories: List[Dict]) -> Dict:
        """Generate a daily schedule based on persona, map info, and memories"""
        # Teacher follows a more structured schedule based on teaching hours
        schedule = {}
        
        # Load the general schedule template
        with open('configs/schedule.json', 'r', encoding='utf-8') as f:
            schedule_template = json.load(f)
        
        # Generate schedule for each time period
        for period in schedule_template['schedule_template']:
            period_info = schedule_template['schedule_template'][period]
            
            # Check if this is a teaching period
            if period in self.schedule_preferences.get('teaching_hours', []):
                schedule[period] = {
                    'activity': 'teaching',
                    'location': self.schedule_preferences.get('preferred_locations', ['classroom'])[0],
                    'topic': self._determine_teaching_topic(date, period, previous_memories)
                }
            else:
                # For non-teaching periods, follow general schedule
                schedule[period] = {
                    'activity': period_info['mandatory'].get(self._get_day_of_week(date), 'optional_activity'),
                    'location': period_info.get('default_location', 'classroom')
                }
        
        # Store the generated schedule
        self.current_schedule = schedule
        return schedule
    
    def _get_day_of_week(self, date_str: str) -> str:
        """Get day of week from date string"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%A').lower()
        except:
            # Default to monday if parsing fails
            return 'monday'
    
    def _determine_teaching_topic(self, date: str, period: str, previous_memories: List[Dict]) -> str:
        """Determine what topic to teach based on curriculum and student needs"""
        # For now, return a general topic - in full implementation this would use knowledge base
        topics = self.knowledge_base.get_topics()
        if topics:
            # Simple selection based on date
            day_index = (datetime.fromisoformat(date.replace('Z', '+00:00')).day - 1) % len(topics)
            return topics[day_index]
        return "General Mathematics"
    
    def generate_curriculum(self, total_days: int) -> List[Dict]:
        """Generate a curriculum based on total days and knowledge base content"""
        curriculum = []
        
        # Get all available topics from knowledge base
        topics = self.knowledge_base.get_topics()
        
        if not topics:
            # Default topics if knowledge base is empty
            topics = ["Introduction to Mathematics", "Algebra Basics", "Geometry Fundamentals", 
                     "Calculus Introduction", "Statistics Overview", "Advanced Topics"]
        
        # Distribute topics across the days
        for day in range(total_days):
            topic_index = day % len(topics)
            curriculum.append({
                "day": day + 1,
                "date": (datetime.now().replace(day=1) + 
                        datetime.timedelta(days=day)).isoformat(),
                "topic": topics[topic_index],
                "difficulty": self._get_difficulty_for_topic(topics[topic_index]),
                "objectives": self._get_learning_objectives(topics[topic_index])
            })
        
        return curriculum
    
    def _get_difficulty_for_topic(self, topic: str) -> str:
        """Get difficulty level for a topic"""
        # Map topics to difficulty levels
        difficulty_map = {
            "Introduction to Mathematics": "beginner",
            "Algebra Basics": "beginner",
            "Geometry Fundamentals": "beginner",
            "Calculus Introduction": "intermediate",
            "Statistics Overview": "intermediate",
            "Advanced Topics": "advanced"
        }
        return difficulty_map.get(topic, "intermediate")
    
    def _get_learning_objectives(self, topic: str) -> List[str]:
        """Get learning objectives for a topic"""
        objectives_map = {
            "Introduction to Mathematics": [
                "Understand basic mathematical concepts",
                "Learn fundamental operations",
                "Develop problem-solving skills"
            ],
            "Algebra Basics": [
                "Solve linear equations",
                "Understand variables and expressions",
                "Apply algebraic principles"
            ],
            "Geometry Fundamentals": [
                "Recognize geometric shapes",
                "Understand properties of shapes",
                "Apply geometric theorems"
            ],
            "Calculus Introduction": [
                "Understand limits and continuity",
                "Learn differentiation basics",
                "Apply calculus to problems"
            ],
            "Statistics Overview": [
                "Interpret data sets",
                "Calculate basic statistics",
                "Understand probability concepts"
            ],
            "Advanced Topics": [
                "Apply complex mathematical concepts",
                "Solve challenging problems",
                "Prepare for advanced study"
            ]
        }
        return objectives_map.get(topic, ["Learn about the topic", "Practice related problems"])
    
    def teach_student(self, student_name: str, topic: str) -> str:
        """Teach a student a specific topic"""
        # Retrieve relevant information from knowledge base
        knowledge_items = self.knowledge_base.search(topic)
        
        if not knowledge_items:
            return f"Sorry, I don't have detailed information about {topic} right now."
        
        # Select the most relevant knowledge item
        selected_knowledge = knowledge_items[0]
        
        # Generate teaching response using LLM
        prompt = f"""
        {self.get_system_prompt()}
        
        You are teaching {student_name} about: {topic}
        Here is relevant information: {selected_knowledge['content']}
        
        Provide an explanation that is clear and appropriate for the student's level.
        """
        
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Explain {topic} to {student_name}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Record the interaction
        self.student_interactions.append({
            "student": student_name,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "response": response.content
        })
        
        # Update teaching experience
        self.teaching_experience += 1
        
        return response.content
    
    def answer_question(self, student_name: str, question: str) -> str:
        """Answer a student's question"""
        # Search knowledge base for relevant information
        knowledge_items = self.knowledge_base.search(question)
        
        # Prepare context for LLM
        context = f"Question from {student_name}: {question}\n"
        if knowledge_items:
            context += f"Relevant information: {[item['content'] for item in knowledge_items[:2]]}"
        
        prompt = f"""
        {self.get_system_prompt()}
        
        {context}
        
        Provide a helpful and accurate answer to the student's question.
        """
        
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=question)
        ]
        
        response = self.llm.invoke(messages)
        
        # Record the interaction
        self.student_interactions.append({
            "student": student_name,
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "response": response.content
        })
        
        return response.content