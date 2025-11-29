"""
Expert Agent Class
"""
from .base_agent import BaseAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from typing import List
import random


class ExpertAgent(BaseAgent):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator):
        super().__init__(name, memory, world)
        self.role = "Expert"
        self.expertise = [
            "Mathematics", "Science", "History", "Literature", 
            "Philosophy", "Technology", "Economics", "Psychology"
        ]
        self.current_expertise = random.choice(self.expertise)
        
    def interact(self, other_agents: List[BaseAgent], topic: str = None):
        """
        Interact with other agents, providing expert knowledge
        """
        if topic is None:
            topic = f"General knowledge about {self.current_expertise}"
        
        prompt = f"Discuss {topic} with the following agents: {[agent.name for agent in other_agents]}"
        
        # Get response from LLM
        response = self.get_response(prompt, f"Your role is an expert in {self.current_expertise}.")
        
        # Remember the interaction
        self.remember(f"Discussed {topic} with {[agent.name for agent in other_agents]}")
        
        print(f"{self.name} (Expert): {response}")
        return response
    
    def teach_student(self, student_agent, topic: str):
        """
        Teach a specific student on a topic
        """
        prompt = f"Explain {topic} to {student_agent.name} in an educational way."
        response = self.get_response(prompt, f"You are an expert teaching {topic}.")
        
        # Remember the teaching interaction
        self.remember(f"Taught {topic} to {student_agent.name}")
        student_agent.remember(f"Learned {topic} from {self.name}")
        
        print(f"{self.name} (Expert) to {student_agent.name}: {response}")
        return response
    
    def interact_with_students(self, students: List[BaseAgent]):
        """
        Main interaction loop with students
        """
        topics = [
            "the importance of critical thinking",
            "how to approach complex problems",
            "the relationship between science and society",
            "the value of continuous learning",
            "how to evaluate information sources"
        ]
        
        for i in range(3):  # 3 rounds of interaction
            topic = random.choice(topics)
            print(f"\n--- Round {i+1}: Discussing '{topic}' ---")
            
            # Expert initiates the discussion
            expert_response = self.interact(students, topic)
            
            # Students respond
            for student in students:
                student_response = student.interact([self] + [s for s in students if s != student], topic)
                # Add a small delay or separator between responses
                print()