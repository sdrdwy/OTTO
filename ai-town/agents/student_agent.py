"""
Student Agent Class
"""
from .base_agent import BaseAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from typing import List
import random


class StudentAgent(BaseAgent):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator):
        super().__init__(name, memory, world)
        self.role = "Student"
        self.learning_goals = [
            "understanding complex concepts",
            "developing critical thinking",
            "improving problem-solving skills",
            "expanding knowledge base",
            "enhancing communication skills"
        ]
        self.current_goal = random.choice(self.learning_goals)
        self.knowledge_level = random.randint(1, 10)  # Random knowledge level 1-10
        
    def interact(self, other_agents: List[BaseAgent], topic: str = None):
        """
        Interact with other agents as a student (this method is still used for some interactions)
        """
        if topic is None:
            topic = "general learning"
        
        # Determine the main agent to interact with (prefer expert if available)
        main_interactant = None
        for agent in other_agents:
            if hasattr(agent, 'role') and agent.role == "Expert":
                main_interactant = agent
                break
        if main_interactant is None:
            main_interactant = random.choice(other_agents)
        
        prompt = f"Ask questions or discuss {topic} with {main_interactant.name}. Your learning goal is {self.current_goal}. Your knowledge level is {self.knowledge_level}/10."
        
        # Get response from LLM
        response = self.get_response(prompt, f"You are a student with the learning goal of {self.current_goal}.")
        
        # Remember the interaction
        self.remember(f"Discussed {topic} with {main_interactant.name}, focusing on {self.current_goal}", "conversation")
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def interact_with_group(self, expert_agent, other_students, topic: str = None):
        """
        Interact in a group setting, responding to the expert and other students
        """
        if topic is None:
            topic = "general learning"
        
        other_student_names = [s.name for s in other_students]
        expert_name = expert_agent.name
        
        prompt = f"Participate in a group discussion about {topic} with {expert_name} and fellow students {other_student_names}. Share your thoughts, ask questions, and engage with others' ideas. Your learning goal is {self.current_goal}."
        
        # Get response from LLM
        response = self.get_response(prompt, f"You are a student participating in a group discussion about {topic}, with the learning goal of {self.current_goal}.")
        
        # Remember the interaction
        self.remember(f"Participated in group discussion about {topic} with {expert_name} and {other_student_names}", "group_discussion")
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def share_opinion(self, topic: str, other_agents: List[BaseAgent]):
        """
        Share an opinion with the group
        """
        agent_names = [agent.name for agent in other_agents]
        prompt = f"Share your opinion about {topic} with {agent_names}. Express your perspective and reasoning."
        
        response = self.get_response(prompt, f"You are sharing your opinion about {topic}.")
        self.remember(f"Shared opinion about {topic} with {agent_names}", "opinion")
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def ask_group_question(self, topic: str, other_agents: List[BaseAgent]):
        """
        Ask a question to the group
        """
        agent_names = [agent.name for agent in other_agents]
        prompt = f"Ask a thought-provoking question about {topic} to {agent_names}."
        
        response = self.get_response(prompt, f"You are asking a question about {topic} to the group.")
        self.remember(f"Asked question about {topic} to {agent_names}", "question")
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def ask_question(self, expert_agent, topic: str):
        """
        Ask a specific question to the expert
        """
        prompt = f"Ask {expert_agent.name} a thoughtful question about {topic}."
        response = self.get_response(prompt, f"You are a student asking questions to learn about {topic}.")
        
        # Remember the interaction
        self.remember(f"Asked a question about {topic} to {expert_agent.name}", "question")
        expert_agent.remember(f"Answered a question from {self.name} about {topic}", "teaching")
        
        print(f"{self.name} (Student) to {expert_agent.name}: {response}")
        return response