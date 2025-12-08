import json
import random
from typing import Dict, List, Any
from langchain_community.chat_models.tongyi import ChatTongyi
from .agent import Agent
from ..configs.config_loader import ConfigLoader
from ..knowledge_base.knowledge_manager import KnowledgeManager


class TeacherAgent(Agent):
    def __init__(self, config_file: str):
        super().__init__(config_file)
        self.knowledge_manager = KnowledgeManager()
        self.curriculum = {}
        self.generate_curriculum()
    
    def generate_curriculum(self):
        """
        Generate a curriculum based on the total number of days and knowledge base
        """
        # Load knowledge base
        knowledge_segments = self.knowledge_manager.retrieve_all_knowledge()
        
        # Distribute knowledge across days
        total_knowledge_items = len(knowledge_segments)
        days_per_topic = max(1, total_knowledge_items // 5)  # Roughly divide into 5 sections
        
        curriculum = {}
        for i, knowledge_item in enumerate(knowledge_segments):
            day_index = (i // days_per_topic) + 1
            if day_index not in curriculum:
                curriculum[f"day_{day_index}"] = []
            curriculum[f"day_{day_index}"].append(knowledge_item)
        
        self.curriculum = curriculum
        return curriculum
    
    def teach_class(self, students: List[str], day_num: int) -> str:
        """
        Teach a class to students based on the curriculum for the day
        """
        day_key = f"day_{day_num}"
        if day_key in self.curriculum and self.curriculum[day_key]:
            # Select knowledge for today's lesson
            today_knowledge = self.curriculum[day_key][0]  # Take first item for simplicity
            
            teaching_prompt = f"""
            As {self.name}, a {self.role}, teach the following concept to students: {students}.
            
            KNOWLEDGE TO TEACH:
            Subject: {today_knowledge.get('subject', 'N/A')}
            Topic: {today_knowledge.get('topic', 'N/A')}
            Content: {today_knowledge.get('content', 'N/A')}
            Difficulty: {today_knowledge.get('difficulty', 'N/A')}
            
            PERSONA:
            - Personality: {self.personality}
            - Teaching style: {self.dialogue_style}
            
            Create an engaging lesson that explains the concept clearly.
            """
            
            try:
                response = self.llm.invoke(teaching_prompt)
                
                # Record teaching activity in memory
                self.memory_manager.add_memory({
                    "type": "teaching_session",
                    "timestamp": "current_time",  # Would be actual timestamp in real implementation
                    "topic": today_knowledge.get('topic', 'N/A'),
                    "students": students,
                    "lesson_content": response.content
                })
                
                return response.content
            except Exception as e:
                print(f"Error during teaching session: {e}")
                return f"Today's lesson on {today_knowledge.get('topic', 'the subject')} will cover fundamental concepts."
        else:
            return "Review day - discussing previously learned material."
    
    def create_daily_schedule(self, day_num: int, total_days: int, world_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Override to create a schedule that includes teaching responsibilities
        """
        # Get current date context
        date_context = f"Day {day_num} of {total_days}. Today's curriculum covers: {[item.get('topic', '') for item in self.curriculum.get(f'day_{day_num}', [])[:2]]}"
        
        # Retrieve recent memories to inform decision making
        recent_memories = self.memory_manager.search_memories("recent_activities", limit=5)
        
        # Get map information
        map_info = world_info.get('map', {})
        locations = [loc['name'] for loc in map_info.get('locations', [])]
        
        # Get current day's global schedule
        daily_schedule = world_info.get('schedule', {}).get('daily_schedule', {})
        
        # Prepare prompt for schedule creation
        prompt = f"""
        As {self.name}, a {self.role}, create your daily schedule for {date_context}.
        
        PERSONA:
        - Personality: {self.personality}
        - Schedule habits: {', '.join(self.schedule_habits)}
        
        WORLD INFORMATION:
        - Locations available: {', '.join(locations)}
        - Global schedule for today: {daily_schedule}
        
        PREVIOUS MEMORIES:
        {recent_memories}
        
        Remember that as a teacher, you need to plan time for:
        - Teaching classes (in classroom)
        - Preparing lessons (possibly in library)
        - Interacting with students
        - Personal rest time
        
        Create a schedule that aligns with your persona and habits while respecting the global schedule.
        Return a dictionary mapping time periods to activities and locations.
        
        Time periods are: morning_1, morning_2, afternoon_1, afternoon_2, evening
        Each activity should specify both the activity type and the location.
        """
        
        # Generate schedule using LLM
        try:
            response = self.llm.invoke(prompt)
            # For now, we'll return a structured schedule based on teacher responsibilities
            schedule = {
                "morning_1": {"activity": "prepare_lessons", "location": "library"},
                "morning_2": {"activity": "teach_class", "location": "classroom"},
                "afternoon_1": {"activity": "teach_class", "location": "classroom"},
                "afternoon_2": {"activity": "student_consultation", "location": "classroom"},
                "evening": {"activity": "rest", "location": "dormitory"}
            }
            
            # Adjust based on mandatory schedule requirements
            for period, details in daily_schedule.items():
                if details.get('mandatory', False):
                    if 'attend_class' in details.get('default', ''):
                        schedule[period] = {"activity": "teach_class", "location": "classroom"}
                    elif 'rest' in details.get('default', ''):
                        schedule[period] = {"activity": "rest", "location": "dormitory"}
            
            self.daily_schedule = schedule
            return schedule
            
        except Exception as e:
            print(f"Error generating schedule for {self.name}: {e}")
            # Fallback to a default teacher schedule
            return {
                "morning_1": {"activity": "prepare_lessons", "location": "library"},
                "morning_2": {"activity": "teach_class", "location": "classroom"},
                "afternoon_1": {"activity": "teach_class", "location": "classroom"},
                "afternoon_2": {"activity": "student_consultation", "location": "classroom"},
                "evening": {"activity": "rest", "location": "dormitory"}
            }
    
    def generate_exam_questions(self) -> List[Dict[str, str]]:
        """
        Generate exam questions based on the curriculum
        """
        exam_questions = []
        
        # Get all knowledge segments across all days
        all_knowledge = []
        for day_knowledge in self.curriculum.values():
            all_knowledge.extend(day_knowledge)
        
        # Create exam questions from knowledge
        for i, knowledge_item in enumerate(all_knowledge[:10]):  # Limit to 10 questions
            question_prompt = f"""
            Based on this knowledge item, create an exam question:
            Subject: {knowledge_item.get('subject', 'N/A')}
            Topic: {knowledge_item.get('topic', 'N/A')}
            Content: {knowledge_item.get('content', 'N/A')}
            
            Create a clear, well-formulated exam question that tests understanding of this concept.
            Also provide a brief answer.
            """
            
            try:
                response = self.llm.invoke(question_prompt)
                
                exam_questions.append({
                    "question_id": i+1,
                    "subject": knowledge_item.get('subject', 'N/A'),
                    "topic": knowledge_item.get('topic', 'N/A'),
                    "question": f"Question {i+1}: {response.content[:200]}...",
                    "answer": "Answer would be generated based on the knowledge content"
                })
            except Exception as e:
                print(f"Error generating exam question: {e}")
                exam_questions.append({
                    "question_id": i+1,
                    "subject": knowledge_item.get('subject', 'N/A'),
                    "topic": knowledge_item.get('topic', 'N/A'),
                    "question": f"Question {i+1}: Basic question about {knowledge_item.get('topic', 'the topic')}",
                    "answer": "Answer would be generated based on the knowledge content"
                })
        
        return exam_questions