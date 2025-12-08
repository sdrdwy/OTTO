import json
import random
from typing import Dict, List, Any
from .agent_base import BaseAgent
from memory.memory_manager import MemoryManager


class ExpertAgent(BaseAgent):
    def __init__(self, config_path: str, memory_manager: MemoryManager, knowledge_base_path: str):
        super().__init__(config_path, memory_manager)
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.teaching_outline = []

    def load_knowledge_base(self, knowledge_base_path: str) -> List[Dict[str, Any]]:
        """Load knowledge base from JSONL file."""
        knowledge_base = []
        with open(knowledge_base_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    knowledge_base.append(json.loads(line.strip()))
        return knowledge_base

    def generate_teaching_outline(self, total_days: int) -> List[Dict[str, Any]]:
        """Generate a teaching outline based on total days and knowledge base content."""
        # Group knowledge by topic
        topics = {}
        for item in self.knowledge_base:
            topic = item.get("topic", "General")
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(item)
        
        # Create a basic outline for the simulation period
        self.teaching_outline = []
        topics_list = list(topics.keys())
        
        for day in range(total_days):
            topic_idx = day % len(topics_list)
            current_topic = topics_list[topic_idx]
            related_knowledge = topics[current_topic]
            
            # Select some knowledge items for this day
            daily_knowledge = random.sample(
                related_knowledge, 
                min(3, len(related_knowledge))
            ) if related_knowledge else []
            
            outline_item = {
                "day": day + 1,
                "topic": current_topic,
                "content": [item["content"] for item in daily_knowledge],
                "activities": [
                    f"Introduce concept: {item['content'][:50]}..." 
                    for item in daily_knowledge
                ]
            }
            self.teaching_outline.append(outline_item)
        
        return self.teaching_outline

    def teach(self, student_agents: List[BaseAgent], day: int):
        """Conduct a teaching session based on the teaching outline."""
        if day <= len(self.teaching_outline):
            daily_outline = self.teaching_outline[day - 1]
            topic = daily_outline["topic"]
            content = daily_outline["content"]
            
            teaching_content = f"Today's lesson: {topic}. Key points: {', '.join(content[:2])}"
            
            # Add teaching memory
            self.memory_manager.add_memory(self.name, teaching_content, "teaching")
            
            # Each student receives the knowledge
            for student in student_agents:
                student.memory_manager.add_memory(
                    student.name, 
                    f"Learned about {topic}: {content[0] if content else 'Basic concepts'}", 
                    "learning"
                )
            
            return teaching_content
        return "No planned lesson for today."

    def answer_question(self, question: str) -> str:
        """Answer a question based on the knowledge base."""
        # Search knowledge base for relevant information
        relevant_knowledge = []
        for item in self.knowledge_base:
            if question.lower() in item.get("content", "").lower() or \
               item.get("topic", "").lower() in question.lower():
                relevant_knowledge.append(item)
        
        if relevant_knowledge:
            # Return the most relevant piece of knowledge
            selected = random.choice(relevant_knowledge)
            answer = f"Based on my knowledge: {selected['content']}"
        else:
            # Try to find related topics
            related_topics = []
            for item in self.knowledge_base:
                if any(word in item.get("content", "").lower() for word in question.lower().split()):
                    related_topics.append(item)
            
            if related_topics:
                selected = random.choice(related_topics)
                answer = f"I found related information: {selected['content']}. Could this help?"
            else:
                answer = "I don't have specific knowledge about that topic, but I can try to help with general guidance."
        
        # Add to memory
        self.memory_manager.add_memory(
            self.name, 
            f"Answered question '{question}' with: {answer}", 
            "teaching"
        )
        
        return answer

    def generate_dialogue_response(self, topic: str, dialogue_history: List[Dict[str, str]], 
                                 other_agent_name: str) -> str:
        """Generate a dialogue response based on personality, knowledge, and context."""
        # If the topic relates to the agent's expertise, use knowledge base
        if any(topic.lower().find(kw) != -1 for kw in ["math", "algebra", "geometry", "calculus", "trigonometry"]):
            # Search for relevant knowledge
            relevant_knowledge = [item for item in self.knowledge_base 
                                if topic.lower() in item.get("content", "").lower() or 
                                item.get("topic", "").lower() in topic.lower()]
            
            if relevant_knowledge:
                knowledge = random.choice(relevant_knowledge)
                response = f"As a teacher, I can explain: {knowledge['content']}"
            else:
                response = f"That's an interesting point about {topic}, {other_agent_name}. What specifically would you like to know?"
        else:
            # Regular response based on personality
            response = f"{other_agent_name}, regarding {topic}: {self.dialogue_style}"
        
        return response