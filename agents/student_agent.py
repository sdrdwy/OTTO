from typing import List, Dict, Any
from .agent_base import BaseAgent
from memory.memory_manager import MemoryManager


class StudentAgent(BaseAgent):
    def __init__(self, config_path: str, memory_manager: MemoryManager):
        super().__init__(config_path, memory_manager)
        self.knowledge_learned = []

    def generate_dialogue_response(self, topic: str, dialogue_history: List[Dict[str, str]], 
                                 other_agent_name: str) -> str:
        """Generate a dialogue response based on personality and context."""
        # Get recent memories to inform the response
        recent_memories = self.memory_manager.get_recent_memories(self.name, 3)
        
        if "math" in topic.lower() or "algebra" in topic.lower() or "geometry" in topic.lower():
            # Student might ask questions about the topic
            if "struggles" in self.personality or "quiet" in self.personality:
                response = f"{other_agent_name}, I'm not sure I understand {topic} completely. Could you explain it differently?"
            elif "curious" in self.personality or "eager" in self.personality:
                response = f"That's interesting about {topic}, {other_agent_name}! Could you tell me more?"
            elif "confident" in self.personality or "competitive" in self.personality:
                response = f"I think I know about {topic}, {other_agent_name}. Here's what I understand..."
            else:
                response = f"{other_agent_name}, regarding {topic}: {self.dialogue_style}"
        else:
            # Regular response based on personality
            response = f"{other_agent_name}, about {topic}: {self.dialogue_style}"
        
        return response

    def learn_from_teacher(self, lesson_content: str):
        """Process and store knowledge received from the teacher."""
        self.knowledge_learned.append(lesson_content)
        self.memory_manager.add_memory(
            self.name, 
            f"Learned: {lesson_content}", 
            "learning"
        )

    def ask_question(self, teacher: 'ExpertAgent', question: str) -> str:
        """Ask a question to the teacher and process the answer."""
        answer = teacher.answer_question(question)
        
        # Store the Q&A in memory
        qa_record = f"Q: {question}, A: {answer}"
        self.memory_manager.add_memory(
            self.name, 
            qa_record, 
            "learning"
        )
        
        return answer