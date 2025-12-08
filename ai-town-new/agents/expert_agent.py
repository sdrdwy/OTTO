import json
from typing import Dict, List, Any
from .base_agent import BaseAgent


class ExpertAgent(BaseAgent):
    def __init__(self, config_path: str, knowledge_base_path: str):
        super().__init__(config_path)
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.curriculum = []
        
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load the knowledge base from JSONL file"""
        kb = []
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        kb.append(json.loads(line))
        except FileNotFoundError:
            print(f"Knowledge base file not found: {self.knowledge_base_path}")
        return kb

    def generate_curriculum(self, total_days: int) -> List[Dict[str, Any]]:
        """Generate a curriculum based on knowledge base and total simulation days"""
        # Calculate how to distribute knowledge across the simulation days
        topics_per_day = max(1, len(self.knowledge_base) // total_days)
        
        curriculum = []
        day_count = 0
        
        for i, knowledge in enumerate(self.knowledge_base):
            day_index = i // topics_per_day
            if day_index >= total_days:
                day_index = total_days - 1  # Assign remaining topics to the last day
                
            # Ensure we have an entry for this day
            while len(curriculum) <= day_index:
                curriculum.append({
                    "day": len(curriculum),
                    "topics": []
                })
            
            curriculum[day_index]["topics"].append(knowledge)
        
        self.curriculum = curriculum
        return curriculum

    def teach_student(self, student_agent: BaseAgent, topic: str):
        """Teach a student about a specific topic using knowledge base"""
        # Find relevant information in knowledge base
        relevant_knowledge = []
        topic_lower = topic.lower()
        
        for item in self.knowledge_base:
            if topic_lower in item['topic'].lower() or topic_lower in item['content'].lower():
                relevant_knowledge.append(item)
        
        if not relevant_knowledge:
            # If no specific topic found, provide general information
            relevant_knowledge = self.knowledge_base[:3]  # First 3 items as default
        
        # Create teaching content
        teaching_content = ""
        for knowledge in relevant_knowledge:
            teaching_content += f"Topic: {knowledge['topic']}\nContent: {knowledge['content']}\n\n"
        
        # Add to student's memory
        student_agent.add_memory(
            f"Received teaching from {self.name} about: {teaching_content[:100]}...", 
            importance=0.9, 
            metadata={"type": "teaching", "source": self.name, "topic": topic}
        )
        
        # Add to expert's memory
        self.add_memory(
            f"Taught {student_agent.name} about: {topic}", 
            importance=0.7, 
            metadata={"type": "teaching", "student": student_agent.name, "topic": topic}
        )

    def answer_question(self, student_agent: BaseAgent, question: str) -> str:
        """Answer a student's question using the knowledge base"""
        # Search knowledge base for relevant information
        relevant_info = []
        question_lower = question.lower()
        
        for item in self.knowledge_base:
            if (question_lower in item['topic'].lower() or 
                question_lower in item['content'].lower() or 
                any(keyword.lower() in question_lower for keyword in item['topic'].split())):
                relevant_info.append(item)
        
        if relevant_info:
            # Construct answer from relevant knowledge
            answer_parts = [f"Based on my knowledge, here's information about '{question}':"]
            for info in relevant_info[:2]:  # Use first 2 relevant items
                answer_parts.append(f"- {info['topic']}: {info['content'][:200]}...")
            
            answer = "\n".join(answer_parts)
        else:
            answer = f"I don't have specific information about '{question}' in my knowledge base, but I can discuss related topics."
        
        # Add to student's memory
        student_agent.add_memory(
            f"Asked {self.name}: {question}. Received answer: {answer[:100]}...", 
            importance=0.6, 
            metadata={"type": "question_answer", "source": self.name, "question": question}
        )
        
        # Add to expert's memory
        self.add_memory(
            f"Answered {student_agent.name}'s question: {question}", 
            importance=0.6, 
            metadata={"type": "question_answer", "student": student_agent.name, "question": question}
        )
        
        return answer

    def generate_daily_schedule(self, date: str, map_info: Dict, other_memories: List[str] = None) -> Dict[str, Any]:
        """Override to generate expert-specific schedule based on curriculum"""
        if other_memories is None:
            other_memories = []
        
        # Get recent memories as context
        recent_memories = [mem.content for mem in self.long_term_memory[-10:]]
        all_memories = recent_memories + other_memories
        
        # Determine today's topics from curriculum based on date
        # Extract day number from date string (assuming format YYYY-MM-DD)
        try:
            date_parts = date.split('-')
            day_of_simulation = int(date_parts[-1]) % 10  # Using day of month as simulation day
        except:
            day_of_simulation = 0
            
        today_topics = []
        if self.curriculum and day_of_simulation < len(self.curriculum):
            today_topics = [topic['topic'] for topic in self.curriculum[day_of_simulation].get('topics', [])]
        
        # Create prompt for schedule generation
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"You are {self.name}, a {self.role} and expert in {self.config.get('teaching_subject', 'Computer Science')}. Your personality: {self.personality['character_setting']}. Your behavior patterns: {', '.join(self.personality['behavior_patterns'])}. Your goals: {', '.join(self.personality['goals'])}. Today's topics to cover: {', '.join(today_topics)}. Based on this, the map information, and your past memories, create a daily schedule for {date}."),
            HumanMessage(content=f"Map information: {json.dumps(map_info, ensure_ascii=False)}\n\nPast memories: {all_memories}\n\nSchedule habits: {self.schedule_habits}\n\nGenerate a daily schedule for the following time periods: morning_class_1, morning_class_2, afternoon_class_1, afternoon_class_2, evening. For each period, specify the location and activity, considering that as an expert you may need to prepare lessons, teach, or engage with students.")
        ])
        
        # Generate schedule using LLM
        chain = prompt | self.llm
        response = chain.invoke({})
        
        # For now, return a default expert schedule
        expert_schedule = {
            "date": date,
            "schedule": {
                "morning_class_1": {"location": "classroom", "activity": "teaching_session"},
                "morning_class_2": {"location": "classroom", "activity": "teaching_session"},
                "afternoon_class_1": {"location": "library", "activity": "preparing_lessons"},
                "afternoon_class_2": {"location": "classroom", "activity": "office_hours"},
                "evening": {"location": "dormitory", "activity": "research"}
            }
        }
        
        return expert_schedule