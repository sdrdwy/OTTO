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
        Interact with multiple agents in a group discussion
        """
        if topic is None:
            topic = f"General knowledge about {self.current_expertise}"
        
        agent_names = [agent.name for agent in other_agents]
        prompt = f"Facilitate a group discussion about {topic} with the following agents: {agent_names}. Encourage diverse perspectives and meaningful exchanges."
        
        # Get response from LLM
        response = self.get_response(prompt, f"Your role is an expert in {self.current_expertise}, facilitating a group discussion.")
        
        # Remember the interaction
        self.remember(f"Facilitated group discussion about {topic} with {agent_names}", "discussion")
        
        print(f"{self.name} (Expert): {response}")
        return response
    
    def teach_student(self, student_agent, topic: str):
        """
        Teach a specific student on a topic
        """
        prompt = f"Explain {topic} to {student_agent.name} in an educational way."
        response = self.get_response(prompt, f"You are an expert teaching {topic}.")
        
        # Remember the teaching interaction
        self.remember(f"Taught {topic} to {student_agent.name}", "teaching")
        student_agent.remember(f"Learned {topic} from {self.name}", "learning")
        
        print(f"{self.name} (Expert) to {student_agent.name}: {response}")
        return response
    
    def interact_with_students(self, students: List[BaseAgent]):
        """
        Main interaction loop with students - supports group discussions
        """
        topics = [
            "the importance of critical thinking",
            "how to approach complex problems",
            "the relationship between science and society",
            "the value of continuous learning",
            "how to evaluate information sources",
            "the role of technology in education",
            "ethical considerations in AI development",
            "strategies for effective communication"
        ]
        
        for i in range(3):  # 3 rounds of interaction
            topic = random.choice(topics)
            print(f"\n--- Round {i+1}: Discussing '{topic}' ---")
            
            # Expert initiates the discussion with all students
            expert_response = self.interact(students, topic)
            
            # Students respond in a more interactive way
            for j, student in enumerate(students):
                # Each student can respond to the discussion
                other_students = [s for s in students if s != student]
                student_response = student.interact_with_group(self, other_students, topic)
                # Add a small delay or separator between responses
                print()

    def facilitate_debate(self, students: List[BaseAgent], topic: str):
        """
        Facilitate a debate between students on a controversial topic
        """
        student_names = [student.name for student in students]
        prompt = f"Facilitate a structured debate about {topic} between {student_names}. Present different viewpoints and encourage critical thinking."
        
        response = self.get_response(prompt, f"You are an expert facilitating a debate on {topic}.")
        self.remember(f"Facilitated debate about {topic} among {student_names}", "debate")
        
        print(f"{self.name} (Expert): {response}")
        return response

    def organize_group_activity(self, students: List[BaseAgent], activity: str):
        """
        Organize a group activity for students
        """
        student_names = [student.name for student in students]
        prompt = f"Organize a {activity} for {student_names}. Provide instructions and facilitate the activity."
        
        response = self.get_response(prompt, f"You are organizing a {activity} for students.")
        self.remember(f"Organized {activity} for {student_names}", "activity")
        
        print(f"{self.name} (Expert): {response}")
        return response