import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base_agent import BaseAgent


class StudentAgent(BaseAgent):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.learning_goals = self.config.get('learning_goals', [])
        self.study_hours = self.schedule_preferences.get('study_hours', [])
        self.exam_scores = {}
        
    def generate_daily_schedule(self, date: str, map_info: Dict, previous_memories: List[Dict]) -> Dict:
        """Generate a daily schedule based on persona, map info, and memories"""
        schedule = {}
        
        # Load the general schedule template
        with open('configs/schedule.json', 'r', encoding='utf-8') as f:
            schedule_template = json.load(f)
        
        # Generate schedule for each time period based on preferences and learning goals
        for period in schedule_template['schedule_template']:
            period_info = schedule_template['schedule_template'][period]
            
            # Determine activity based on student preferences and learning goals
            if period in self.study_hours:
                # This is a preferred study period
                schedule[period] = {
                    'activity': self._determine_study_activity(date, period, previous_memories),
                    'location': self._select_preferred_location(period, map_info)
                }
            else:
                # Follow general schedule but adapt to student preferences
                base_activity = period_info['mandatory'].get(self._get_day_of_week(date), 'optional_activity')
                schedule[period] = {
                    'activity': base_activity,
                    'location': self._select_preferred_location(period, map_info)
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
    
    def _determine_study_activity(self, date: str, period: str, previous_memories: List[Dict]) -> str:
        """Determine what study activity to do based on learning goals and memories"""
        # Check previous memories to see what needs reinforcement
        recent_topics = []
        for memory in previous_memories[-5:]:  # Look at last 5 memories
            if 'content' in memory and ('topic' in memory['content'] or 'math' in memory['content'].lower()):
                recent_topics.append(memory['content'])
        
        if recent_topics:
            # Focus on reinforcing recent topics
            return f"review: {recent_topics[-1][:50]}"
        else:
            # Default to general study
            return "independent study"
    
    def _select_preferred_location(self, period: str, map_info: Dict) -> str:
        """Select location based on preferences and period"""
        preferred_locations = self.schedule_preferences.get('preferred_locations', ['library'])
        
        # Check if any preferred location exists in map
        for location in preferred_locations:
            if location in map_info['locations']:
                return location
        
        # If none of preferred locations exist, return the first location in map
        return list(map_info['locations'].keys())[0] if map_info['locations'] else 'classroom'
    
    def ask_question(self, teacher_name: str, question: str) -> str:
        """Ask a question to a teacher"""
        # This would call the teacher's answer_question method in a full implementation
        # For now, we'll simulate by generating a response
        prompt = f"""
        {self.get_system_prompt()}
        
        You are {self.name} asking {teacher_name}: {question}
        
        Formulate the question in a way that's appropriate to your learning goals: {self.learning_goals}
        """
        
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=question)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content
        
        # Generate memory about asking the question
        self.generate_memory(f"Asked {teacher_name}: {question}", "academic_interaction")
        
        return response_text
    
    def study_topic(self, topic: str) -> str:
        """Study a specific topic"""
        # Generate memory about studying
        self.generate_memory(f"Studied {topic}", "academic_activity")
        
        # For now, just return a confirmation
        return f"{self.name} studied {topic} and made progress on learning goals: {self.learning_goals}"
    
    def take_exam(self, exam_data: Dict) -> Dict:
        """Take an exam and return results"""
        score = 0
        total_points = 0
        
        for question in exam_data['questions']:
            total_points += 20  # Assume each question is worth 20 points
            
            # For now, just give a random score based on student personality
            import random
            if 'diligent' in self.personality['traits'] or 'curious' in self.personality['traits']:
                # These traits improve performance
                score += random.randint(15, 20)
            elif 'introverted' in self.personality['traits']:
                # These might perform differently
                score += random.randint(10, 18)
            else:
                score += random.randint(8, 18)
        
        # Calculate grade
        percentage = (score / total_points) * 100
        grade = self._calculate_grade(percentage, exam_data['grading_scale'])
        
        result = {
            "exam_id": exam_data['exam_id'],
            "student": self.name,
            "score": score,
            "total_points": total_points,
            "percentage": percentage,
            "grade": grade,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store the exam result
        self.exam_scores[exam_data['exam_id']] = result
        
        # Generate memory about taking the exam
        self.generate_memory(f"Took exam {exam_data['exam_id']}, scored {percentage}%, grade {grade}", "academic_assessment")
        
        return result
    
    def _calculate_grade(self, percentage: float, grading_scale: Dict) -> str:
        """Calculate letter grade based on percentage and grading scale"""
        if percentage >= grading_scale.get('A', 90):
            return 'A'
        elif percentage >= grading_scale.get('B', 80):
            return 'B'
        elif percentage >= grading_scale.get('C', 70):
            return 'C'
        elif percentage >= grading_scale.get('D', 60):
            return 'D'
        else:
            return 'F'
    
    def update_learning_goals(self, new_goals: List[str]) -> None:
        """Update learning goals based on experience"""
        self.learning_goals = new_goals
        self.generate_memory(f"Updated learning goals to: {new_goals}", "academic_planning")