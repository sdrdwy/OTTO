"""
Student Agent Class
"""
from .base_agent import BaseAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from typing import List
import random


class StudentAgent(BaseAgent):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator, config_file: str = None):
        super().__init__(name, memory, world, config_file, agent_type="student")
        
        # Initialize student-specific attributes
        self.current_goal = random.choice(self.learning_goals) if self.learning_goals else "understanding complex concepts"
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
        
        # Get relevant memories and knowledge to inform the interaction
        memories = self.get_all_memories()
        knowledge = []
        if hasattr(self, 'knowledge_manager'):
            knowledge = self.knowledge_manager.get_relevant_knowledge("General", topic)
        
        prompt = f"用中文与{main_interactant.name}讨论{topic}。你的学习目标是{self.current_goal}。你的知识水平是{self.knowledge_level}/10。"
        
        # Get response from LLM
        response = self.get_response(prompt, f"你是一个学生，学习目标是{self.current_goal}。")
        
        interaction_memory = f"用中文与{main_interactant.name}讨论了{topic}，重点是{self.current_goal}"
        self.remember(interaction_memory, "conversation", location=self.location)
        main_interactant.remember(f"与{self.name}讨论了{topic}，帮助其学习目标{self.current_goal}", "teaching", location=main_interactant.location)
        
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
        
        prompt = f"参与关于{topic}的小组讨论，与{expert_name}和其他同学{other_student_names}一起。分享你的想法，提出问题，并参与其他人的想法。你的学习目标是{self.current_goal}。"
        
        # Get response from LLM
        response = self.get_response(prompt, f"你是一个学生，正在参与关于{topic}的小组讨论，学习目标是{self.current_goal}。")
        
        # Remember the interaction
        self.remember(f"参与了关于{topic}的小组讨论，与{expert_name}和{other_student_names}", "group_discussion", location=self.location)
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def share_opinion(self, topic: str, other_agents: List[BaseAgent]):
        """
        Share an opinion with the group
        """
        agent_names = [agent.name for agent in other_agents]
        prompt = f"与{agent_names}分享你对{topic}的看法。表达你的观点和推理。"
        
        response = self.get_response(prompt, f"你正在分享对{topic}的看法。")
        self.remember(f"与{agent_names}分享了对{topic}的看法", "opinion", location=self.location)
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def ask_group_question(self, topic: str, other_agents: List[BaseAgent]):
        """
        Ask a question to the group
        """
        agent_names = [agent.name for agent in other_agents]
        prompt = f"向{agent_names}提出一个关于{topic}的发人深省的问题。"
        
        response = self.get_response(prompt, f"你正在向小组提出关于{topic}的问题。")
        self.remember(f"向{agent_names}提出了关于{topic}的问题", "question", location=self.location)
        
        print(f"{self.name} (Student): {response}")
        return response
    
    def ask_question(self, expert_agent, topic: str):
        """
        Ask a specific question to the expert
        """
        prompt = f"向{expert_agent.name}提出一个关于{topic}的深思熟虑的问题。"
        response = self.get_response(prompt, f"你是一个学生，正在提问以了解{topic}。")
        
        # Remember the interaction
        self.remember(f"向{expert_agent.name}提出了关于{topic}的问题", "question", location=self.location)
        expert_agent.remember(f"回答了{self.name}关于{topic}的问题", "teaching", location=expert_agent.location)
        
        print(f"{self.name} (Student) to {expert_agent.name}: {response}")
        return response