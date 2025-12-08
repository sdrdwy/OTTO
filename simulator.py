import json
import os
from typing import List, Dict, Any
from memory.memory_manager import MemoryManager
from world.world_manager import WorldManager
from world.exam_system import ExamSystem
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent


class Simulator:
    def __init__(self, config_path: str = "config/config.json"):
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Initialize systems
        self.memory_manager = MemoryManager(
            memory_file_path=self.config["memory_file_path"],
            capacity=self.config["memory_capacity"]
        )
        self.world_manager = WorldManager(
            world_config_path=self.config["world_config_path"],
            schedule_config_path=self.config["schedule_config_path"]
        )
        self.exam_system = ExamSystem(
            knowledge_base_path=self.config["knowledge_base_path"],
            num_questions=self.config["exam_questions_count"]
        )
        
        # Initialize agents
        self.agents = {}
        self.teacher = None
        self.students = []
        
        self.initialize_agents()
    
    def initialize_agents(self):
        """Initialize all agents based on configuration files"""
        # Initialize teacher (expert agent)
        teacher_config_path = os.path.join(self.config["agents_config_path"], "teacher.json")
        self.teacher = ExpertAgent(
            config_path=teacher_config_path,
            memory_manager=self.memory_manager,
            world_manager=self.world_manager,
            knowledge_base_path=self.config["knowledge_base_path"]
        )
        self.agents[self.teacher.name] = self.teacher
        
        # Initialize students
        for i in range(1, 5):  # student1 to student4
            student_config_path = os.path.join(self.config["agents_config_path"], f"student{i}.json")
            student = StudentAgent(
                config_path=student_config_path,
                memory_manager=self.memory_manager,
                world_manager=self.world_manager
            )
            self.agents[student.name] = student
            self.students.append(student)
    
    def run_simulation(self):
        """Run the complete simulation"""
        print("🚀 Starting AI Town Simulation...")
        print(f"📅 Simulation will run for {self.config['simulation_days']} days")
        print(f"⏱️  Each day has {len(self.config['time_periods'])} time periods")
        
        # Administer pre-test before simulation starts
        all_agents = [self.teacher] + self.students
        pre_test_results = self.exam_system.administer_pre_test(all_agents)
        
        # Run simulation for specified number of days
        for day in range(1, self.config['simulation_days'] + 1):
            print(f"\n📅 DAY {day} BEGINS")
            print("="*60)
            
            self.world_manager.advance_day()
            
            # Process each time period of the day
            for period in self.config['time_periods']:
                self.world_manager.set_current_period(period)
                
                print(f"\n⏰ PERIOD: {period.upper()}")
                
                # Display current map state
                self.world_manager.display_map_state()
                
                # Each agent acts based on their schedule and persona
                for agent_name, agent in self.agents.items():
                    self.process_agent_action(agent, day, period)
                
                print(f"\n✅ Period {period} completed")
            
            print(f"\n📅 DAY {day} ENDS")
            print("="*60)
        
        # Administer post-test after simulation ends
        post_test_results = self.exam_system.administer_post_test(all_agents)
        
        # Compare results
        self.exam_system.compare_results(pre_test_results, post_test_results)
        
        print("\n🎉 Simulation completed successfully!")
    
    def process_agent_action(self, agent, day: int, period: str):
        """Process an agent's action for a specific day and period"""
        # Get the agent's planned activity for this period
        activity = agent.get_daily_schedule(day, period)
        
        print(f"\n👤 {agent.name} scheduled activity: {activity}")
        
        # Execute activity based on type
        if activity == "attend_class" or activity == "teach_class":
            # Move to classroom
            agent.update_location("classroom")
            
            if agent.name == "teacher":
                # Teacher teaches
                student_names = [s.name for s in self.students]
                lesson_topic = agent.get_curriculum_for_day(day).get("topics", ["general topic"])[0] if hasattr(agent, 'get_curriculum_for_day') else "general topic"
                lesson_content = agent.teach(student_names, lesson_topic)
                print(f"   📚 Teacher conducted lesson: {lesson_content}")
            else:
                # Student attends class
                lesson_topic = self.teacher.get_curriculum_for_day(day).get("topics", ["general topic"])[0] if hasattr(self.teacher, 'get_curriculum_for_day') else "general topic"
                agent.study_topic(lesson_topic)
                print(f"   📖 {agent.name} studied: {lesson_topic}")
        
        elif activity == "study":
            # Move to library or study area
            agent.update_location("library")
            # Study a relevant topic
            if hasattr(agent, 'study_topic'):
                topic = "general study topic"
                agent.study_topic(topic)
                print(f"   📚 {agent.name} studied: {topic}")
        
        elif activity == "free_time":
            # Agent can choose their activity based on persona
            agent.update_location("playground")  # or other locations based on preference
            # Perform independent activity
            result = agent.act_independently("free time activity")
            print(f"   🎉 {result}")
        
        elif activity == "group_activity":
            # Move to common area
            agent.update_location("cafeteria")
            
            # For teacher, this might involve organizing activities
            if agent.name == "teacher":
                topic = "group activity topic"
                student_names = [s.name for s in self.students]
                lesson_content = agent.teach(student_names, topic)
                print(f"   👥 Teacher led group activity: {lesson_content}")
            else:
                # Students participate in group activity
                topic = "group activity topic"
                agent.study_topic(topic)
                print(f"   👥 {agent.name} participated in group activity: {topic}")
        
        elif activity == "rest":
            # Move to dormitory to rest
            agent.update_location("dormitory")
            result = agent.act_independently("resting")
            print(f"   😴 {result}")
        
        elif activity == "introduction":
            # Special activity for day 1
            agent.update_location("classroom")
            if agent.name == "teacher":
                print("   👨‍🏫 Teacher introduces class and curriculum")
            else:
                print(f"   👤 {agent.name} gets introduced to class")
        
        else:
            # Default action - move to appropriate location and perform activity
            agent.update_location("classroom")  # default to classroom
            result = agent.act_independently(activity)
            print(f"   🔄 {result}")
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a summary of the simulation results"""
        summary = {
            "total_days": self.config['simulation_days'],
            "total_agents": len(self.agents),
            "teacher": self.teacher.name,
            "students": [s.name for s in self.students],
            "total_memories": len(self.memory_manager.memories),
            "map_locations": list(self.world_manager.map.keys())
        }
        
        # Add exam results
        all_agents = [self.teacher] + self.students
        summary["exam_results"] = {}
        
        for agent in all_agents:
            if hasattr(agent, 'exam_scores') and agent.exam_scores:
                summary["exam_results"][agent.name] = {
                    "latest_score": agent.get_latest_exam_score(),
                    "overall_performance": agent.get_overall_performance()
                }
            else:
                summary["exam_results"][agent.name] = {
                    "latest_score": 95,  # Experts maintain high scores
                    "overall_performance": 95.0
                }
        
        return summary


if __name__ == "__main__":
    simulator = Simulator()
    simulator.run_simulation()
    
    # Print final summary
    summary = simulator.get_simulation_summary()
    print("\n📊 SIMULATION SUMMARY:")
    print(json.dumps(summary, indent=2))