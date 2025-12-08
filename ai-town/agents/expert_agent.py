"""
Expert Agent Class
"""
from .base_agent import BaseAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from typing import List
import random


class ExpertAgent(BaseAgent):
    def __init__(self, name: str, memory: ConversationMemory, world: WorldSimulator, config_file: str = None):
        super().__init__(name, memory, world, config_file, agent_type="expert")
        
        # Initialize expert-specific attributes
        self.current_expertise = random.choice(self.expertise) if self.expertise else "General Knowledge"
        
        # Generate teaching curriculum based on knowledge base and total days
        self.curriculum = self.generate_curriculum()
    
    def generate_curriculum(self):
        """
        Generate a teaching curriculum based on total days and knowledge base
        """
        # For now, return a simple curriculum based on expertise
        curriculum = {}
        
        if self.expertise:
            for i, subject in enumerate(self.expertise[:5]):  # Limit to first 5 expertise areas
                curriculum[f"week_{i+1}"] = {
                    "subject": subject,
                    "topics": [f"Introduction to {subject}", f"Advanced concepts in {subject}", f"Applications of {subject}"],
                    "learning_objectives": [f"Understand basic principles of {subject}", f"Apply {subject} concepts to problems", f"Evaluate {subject} methodologies"]
                }
        
        return curriculum
        
    def interact(self, other_agents: List[BaseAgent], topic: str = None):
        """
        Interact with multiple agents in a group discussion
        """
        if topic is None:
            topic = f"关于{self.current_expertise}的一般知识"
        
        agent_names = [agent.name for agent in other_agents]
        
        # Get relevant memories and knowledge to inform the interaction
        memories = self.get_all_memories()
        knowledge = []
        if hasattr(self, 'knowledge_manager'):
            knowledge = self.knowledge_manager.get_relevant_knowledge(self.current_expertise, topic)
        
        prompt = f"用中文主持关于{topic}的小组讨论，参与的代理有：{agent_names}。鼓励多样化的观点和有意义的交流。"
        
        # Get response from LLM
        response = self.get_response(prompt, f"你的角色是{self.current_expertise}的专家，正在主持小组讨论。")
        
        # Remember the interaction for all agents involved
        interaction_memory = f"主持了关于{topic}的小组讨论，参与的代理有：{agent_names}"
        self.remember(interaction_memory, "discussion", location=self.location)
        
        for agent in other_agents:
            agent.remember(f"参与了关于{topic}的小组讨论，与{self.name}", "learning", location=agent.location)
        
        print(f"{self.name} (Expert): {response}")
        return response
    
    def teach_student(self, student_agent, topic: str):
        """
        Teach a specific student on a topic
        """
        prompt = f"用中文向{student_agent.name}解释{topic}。"
        response = self.get_response(prompt, f"你是一个专家，正在教授{topic}。")
        
        # Remember the teaching interaction
        self.remember(f"向{student_agent.name}教授了{topic}", "teaching", location=self.location)
        student_agent.remember(f"从{self.name}那里学习了{topic}", "learning", location=student_agent.location)
        
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
        prompt = f"用中文主持关于{topic}的辩论，参与的学生有{student_names}。提出不同的观点并鼓励批判性思维。"
        
        response = self.get_response(prompt, f"你正在主持关于{topic}的辩论。")
        self.remember(f"主持了关于{topic}在{self.location}的辩论，参与的学生有{student_names}", "debate", location=self.location)
        
        print(f"{self.name} (Expert): {response}")
        return response

    def organize_group_activity(self, students: List[BaseAgent], activity: str):
        """
        Organize a group activity for students
        """
        student_names = [student.name for student in students]
        prompt = f"为{student_names}组织一个{activity}。提供说明并主持活动。"
        
        response = self.get_response(prompt, f"你正在为学生组织{activity}。")
        self.remember(f"在{self.location}为{student_names}组织了{activity}", "activity", location=self.location)
        
        print(f"{self.name} (Expert): {response}")
        return response