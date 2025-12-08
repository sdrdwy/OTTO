"""
Simulation Manager for AI Town
Coordinates the entire simulation including agents, events, schedules, and logging
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from agents.student_agent import StudentAgent
from agents.expert_agent import ExpertAgent
from memory.conversation_memory import ConversationMemory
from memory.knowledge_base import AgentKnowledgeManager
from world.world_simulator import WorldSimulator
from utils.event_generator import EventGenerator, FestivalManager
from utils.logger import SimulationLogger
from utils.calendar import Calendar
from exam_system import ExamSystem


class SimulationManager:
    def __init__(self, config_file: str = "config_files/system_configs/world_config.json"):
        self.config_file = config_file
        self.load_config()
        
        # Initialize components
        self.world = WorldSimulator()
        self.memory = ConversationMemory()
        self.calendar = Calendar()
        self.event_generator = EventGenerator(self.config_file)
        self.festival_manager = FestivalManager(self.event_generator)
        self.logger = SimulationLogger()
        self.exam_system = ExamSystem()
        
        # Initialize agents
        self.agents: List = []
        self.student_agents: List[StudentAgent] = []
        self.expert_agents: List[ExpertAgent] = []
    
    def load_config(self):
        """Load simulation configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "simulation_days": 30,
                "event_frequency": 14,
                "current_day": 0,
                "time_periods": [
                    "morning_class",
                    "morning_free", 
                    "afternoon_class",
                    "afternoon_free",
                    "evening"
                ],
                "simulation_speed": "real_time", 
                "world_events_enabled": True,
                "festival_enabled": True
            }
    
    def save_config(self):
        """Save simulation configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2, default=str)
    
    def initialize_agents(self):
        """Initialize student and expert agents from config file"""
        # Load agents configuration
        agents_config_path = "config_files/agent_configs/agents_config.json"
        agents_config = {}
        if os.path.exists(agents_config_path):
            with open(agents_config_path, 'r', encoding='utf-8') as f:
                agents_config = json.load(f)
        
        # Create expert agents from config
        experts_list = agents_config.get("experts", [])
        for expert_data in experts_list:
            expert_id = expert_data["id"]
            expert_name = expert_data["name"]
            start_location = expert_data.get("location", "classroom")
            
            # Create expert with persona
            expert = ExpertAgent(expert_name, self.memory, self.world, persona_id=expert_id)
            expert.move_to_location(start_location)  # Experts typically start in classroom
            self.expert_agents.append(expert)
            self.agents.append(expert)
        
        # Create student agents from config
        students_list = agents_config.get("students", [])
        
        for student_data in students_list:
            student_id = student_data["id"]
            student_name = student_data["name"]
            start_location = student_data.get("location", "classroom")
            
            # Create student with persona
            student = StudentAgent(student_name, self.memory, self.world, persona_id=student_id)
            
            # Set student-specific attributes from config
            student.learning_goals = student_data.get("learning_goals", ["study", "improve skills"])
            student.preferred_locations = student_data.get("preferred_locations", ["library", "classroom"])
            student.social_preferences = student_data.get("social_preferences", ["collaborate", "network"])
            student.activity_preferences = student_data.get("activity_preferences", ["study", "practice", "discuss"])
            
            student.move_to_location(start_location)
            self.student_agents.append(student)
            self.agents.append(student)
            
            # Create daily schedule for student using their preferences
            schedule = DailySchedule(student.name)
            self.daily_schedules[student.name] = schedule
    
    def create_daily_schedules(self, date: str):
        """Create daily schedules for all students with their preferences and memory context"""
        # Load total schedule logic from config file
        total_schedule_config_path = "config_files/schedule_configs/total_schedule.json"
        total_schedule_logic = {}
        if os.path.exists(total_schedule_config_path):
            with open(total_schedule_config_path, 'r', encoding='utf-8') as f:
                total_schedule_logic = json.load(f)
        
        for student in self.student_agents:
            # Get student preferences to pass to schedule creation
            agent_preferences = {
                "learning_goals": getattr(student, 'learning_goals', ["study", "improve skills"]),
                "preferred_locations": getattr(student, 'preferred_locations', ["library", "classroom"]),
                "social_preferences": getattr(student, 'social_preferences', ["collaborate", "network"]),
                "activity_preferences": getattr(student, 'activity_preferences', ["study", "practice", "discuss"])
            }
            # Get recent memories to use as context for scheduling
            memory_context = []
            if hasattr(student, 'memory') and student.memory:
                memory_context = student.memory.get_recent_memories(student.name, limit=10)
                # Convert to the expected format (list of dict with content field)
                memory_context = [{"content": mem} for mem in memory_context]
            
            # Create schedule with student's preferences and memory context
            student.create_daily_schedule(date, total_schedule_logic=total_schedule_logic)
    
    def run_simulation(self):
        """Run the entire simulation"""
        print(f"Starting simulation for {self.config['simulation_days']} days...")
        self.logger.log_event("simulation_start", f"Simulation started for {self.config['simulation_days']} days")
        
        # Initialize agents
        self.initialize_agents()
        
        # Administer initial exam before simulation begins
        print("\n" + "="*50)
        print("ADMINISTERING INITIAL EXAM")
        print("="*50)
        self.initial_exam_results = self.exam_system.administer_exam(self.agents)
        self.exam_system.save_exam_results(self.initial_exam_results, "initial_exam_results.json")
        
        # Main simulation loop
        for day in range(self.config['simulation_days']):
            self.config['current_day'] = day
            self.save_config()
            self.event_generator.increment_day()
            
            print(f"\n=== Day {day + 1} ===")
            date_str = (datetime.now() + timedelta(days=day)).date().isoformat()
            
            # Create daily schedules for all students
            self.create_daily_schedules(date_str)
            
            # Check if festival should be generated
            festival = self.festival_manager.check_and_generate_festival()
            if festival:
                print(f"Festival generated: {festival['type']} at {festival['location']}")
                self.logger.log_event("festival", f"Festival: {festival['type']}", 
                                    [agent.name for agent in self.agents], festival['location'])
            
            # Process each time period of the day
            for period in self.config['time_periods']:
                print(f"\n--- {period.upper().replace('_', ' ')} ---")
                
                # Move agents according to their schedule for this period
                self.execute_period_schedule(period, date_str)
                
                # Simulate other activities happening during this time period
                self.simulate_period_activities(period)
                
                # Check for location-based interactions
                interactions = self.world.check_location_interactions()
                
                # Log the period
                self.logger.log_event("time_period", f"{period} period completed", 
                                    [agent.name for agent in self.agents])
            
            # Daily summary
            daily_summary = f"Day {day + 1} completed with {len(self.logger.logs['interactions']) - sum(1 for x in range(day) for _ in self.logger.logs['daily_summaries'] if x < day)} interactions"
            self.logger.log_daily_summary(day, daily_summary)
            
            # Trigger class event if it's a class period
            if day % 2 == 0:  # Every other day, have a class
                if self.expert_agents and self.student_agents:
                    self.world.trigger_class_event(self.expert_agents[0], self.student_agents[:2])
        
        # Administer final exam after simulation ends
        print("\n" + "="*50)
        print("ADMINISTERING FINAL EXAM")
        print("="*50)
        self.final_exam_results = self.exam_system.administer_exam(self.agents)
        self.exam_system.save_exam_results(self.final_exam_results, "final_exam_results.json")
        
        # Compare results
        comparison = self.exam_system.compare_results(self.initial_exam_results, self.final_exam_results)
        print("\n" + "="*50)
        print("EXAM RESULTS COMPARISON")
        print("="*50)
        for agent_name, data in comparison.items():
            print(f"{agent_name}:")
            print(f"  Initial Score: {data['initial_score']:.2%}")
            print(f"  Final Score: {data['final_score']:.2%}")
            print(f"  Improvement: {data['improvement']:.2%} ({data['improvement_percentage']:.2f}%)")
        
        # End simulation
        self.logger.log_event("simulation_end", "Simulation completed")
        self.logger.save_log()
        
        # Print simulation statistics
        stats = self.logger.get_statistics()
        print(f"\nSimulation completed! Statistics:")
        print(f"- Total events: {stats['total_events']}")
        print(f"- Total interactions: {stats['total_interactions']}")
        print(f"- Total movements: {stats['total_movements']}")
        print(f"- Daily summaries: {stats['total_daily_summaries']}")
    
    def execute_period_schedule(self, period: str, date: str):
        """Execute the schedule for a specific time period"""
        for student in self.student_agents:
            # Get the student's schedule for this date and period
            period_schedule = {}
            if date in student.daily_schedule and period in student.daily_schedule[date]:
                period_schedule = [student.daily_schedule[date][period]]
            else:
                # Fallback to default behavior if no schedule exists
                period_schedule = [{}]
            
            if period_schedule and period_schedule[0]:
                # Move student to scheduled location
                target_location = period_schedule[0].get("location", "classroom")
                activity = period_schedule[0].get("activity", "unspecified activity")
                student.move_to_location(target_location)
                
                # Record more detailed memory about the scheduled activity
                detailed_memory = f"Participated in scheduled activity '{activity}' at {target_location} during {period} on {date}. Activity details: {period_schedule[0]}"
                student.remember(detailed_memory, "scheduled_activity")
                
                # If it's a class period and there are experts around, trigger learning
                if "class" in period and self.expert_agents:
                    expert = self.expert_agents[0]
                    if expert.location == student.location:
                        # Students can interact with expert
                        topic = "scheduled_class"
                        student.ask_question(expert, topic)
                        expert.teach_student(student, topic)
            else:
                # Default behavior if no specific schedule
                if "class" in period:
                    # Move to classroom for class
                    student.move_to_location("classroom")
                    student.remember(f"Moved to classroom for {period} period on {date}", "movement")
                elif "free" in period:
                    # Move to a random location for free time
                    import random
                    free_locations = ["library", "park", "cafe"]
                    target_location = random.choice(free_locations)
                    student.move_to_location(target_location)
                    student.remember(f"Moved to {target_location} for free time during {period} on {date}", "movement")
                elif period == "evening":
                    # Go to rest location
                    student.move_to_location("park")  # or home if available
                    student.remember(f"Moved to park for evening rest on {date}", "movement")
        
        # Check for and process any festivals happening today
        active_festivals = self.festival_manager.get_active_festivals()
        for festival in active_festivals:
            if festival.get("active", True):
                # Trigger festival event
                participants = self.student_agents + self.expert_agents
                self.world.trigger_event_at_location(festival["location"], "festival", participants, festival["type"])
                festival["active"] = False  # Mark as processed
    
    def simulate_period_activities(self, period: str):
        """
        Simulate other activities happening during each time period beyond agent interactions
        """
        import random
        
        # Define different activities based on the time period
        period_activities = {
            "morning_class": [
                "早读",
                "晨练", 
                "校园清洁",
                "升旗仪式",
                "早操",
                "晨会"
            ],
            "morning_free": [
                "自由阅读",
                "个人学习",
                "校园漫步",
                "社团活动准备", 
                "与朋友聊天",
                "咖啡厅休闲"
            ],
            "afternoon_class": [
                "实验课",
                "小组讨论",
                "学术讲座", 
                "作业辅导",
                "技能训练",
                "项目展示"
            ],
            "afternoon_free": [
                "体育运动",
                "艺术创作",
                "社团活动",
                "兴趣小组",
                "校园参观", 
                "放松休息"
            ],
            "evening": [
                "晚间自习",
                "反思总结", 
                "日志写作",
                "睡前放松",
                "文化交流",
                "个人时间"
            ]
        }
        
        # Select activities for this period
        activities = period_activities.get(period, ["一般活动"])
        
        # Randomly decide whether to simulate an activity during this period
        if random.random() > 0.3:  # 70% chance of having an activity
            activity = random.choice(activities)
            
            # Select a random location for the activity
            location = random.choice(list(self.world.locations.keys()))
            
            # Create a description of the activity
            activity_description = f"在{location}进行{activity}活动"
            
            print(f"  [其他活动] {activity_description}")
            
            # Record this activity in the simulation
            self.logger.log_event("period_activity", activity_description, 
                                [agent.name for agent in self.agents], location)
            
            # Trigger a world event related to this activity
            event_description = self.world.trigger_event_at_location(
                location, 
                activity, 
                [],  # No specific participants for general activities
                activity
            )

        # Now simulate student-to-student conversations and activities
        # Find students at the same location and have them interact
        location_groups = {}
        for student in self.student_agents:
            if student.location not in location_groups:
                location_groups[student.location] = []
            location_groups[student.location].append(student)
        
        # For each location with multiple students, trigger conversations
        for location, students_at_location in location_groups.items():
            if len(students_at_location) > 1:
                # Students at the same location can have conversations
                print(f"  [学生对话] 在{location}有{len(students_at_location)}名学生进行交流")
                
                # Select 2 random students to have a conversation
                if len(students_at_location) >= 2:
                    selected_students = random.sample(students_at_location, min(2, len(students_at_location)))
                    topic_options = [
                        "学习心得分享",
                        "课程内容讨论", 
                        "兴趣爱好交流",
                        "未来规划",
                        "校园生活",
                        "学术问题探讨"
                    ]
                    conversation_topic = random.choice(topic_options)
                    
                    # Have students engage in conversation
                    student1, student2 = selected_students[0], selected_students[1]
                    
                    # Student 1 initiates conversation
                    prompt = f"用中文与{student2.name}就{conversation_topic}进行交流。"
                    response = student1.get_response(prompt, f"你正在与{student2.name}交流{conversation_topic}。")
                    print(f"  {student1.name}: {response}")
                    
                    # Student 2 responds
                    prompt = f"回应{student1.name}关于{conversation_topic}的分享。"
                    response = student2.get_response(prompt, f"你正在回应{student1.name}关于{conversation_topic}的分享。")
                    print(f"  {student2.name}: {response}")
                    
                    # Record the conversation in both students' memories
                    student1.remember(f"与{student2.name}就{conversation_topic}进行了交流", "conversation", location=student1.location)
                    student2.remember(f"与{student1.name}就{conversation_topic}进行了交流", "conversation", location=student2.location)


if __name__ == "__main__":
    sim_manager = SimulationManager()
    sim_manager.run_simulation()