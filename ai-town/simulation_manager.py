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
from utils.daily_schedule import DailySchedule
from utils.event_generator import EventGenerator, FestivalManager
from utils.logger import SimulationLogger
from utils.calendar import Calendar


class SimulationManager:
    def __init__(self, config_file: str = "config/world_config.json"):
        self.config_file = config_file
        self.load_config()
        
        # Initialize components
        self.world = WorldSimulator()
        self.memory = ConversationMemory()
        self.calendar = Calendar()
        self.event_generator = EventGenerator(self.config_file)
        self.festival_manager = FestivalManager(self.event_generator)
        self.logger = SimulationLogger()
        
        # Initialize agents
        self.agents: List = []
        self.student_agents: List[StudentAgent] = []
        self.expert_agents: List[ExpertAgent] = []
        
        # Initialize daily schedules
        self.daily_schedules: Dict[str, DailySchedule] = {}
    
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
        # Load students configuration
        students_config_path = "config/students_config.json"
        students_config = {}
        if os.path.exists(students_config_path):
            with open(students_config_path, 'r', encoding='utf-8') as f:
                students_config = json.load(f)
        
        # Create expert agent
        expert = ExpertAgent("ProfessorSmith", self.memory, self.world, persona_id="math_expert")
        expert.move_to_location("classroom")  # Experts typically start in classroom
        self.expert_agents.append(expert)
        self.agents.append(expert)
        
        # Create student agents from config
        students_list = students_config.get("students", [])
        locations = students_config.get("locations", ["library", "classroom", "park", "cafe", "lab"])
        
        for student_data in students_list:
            student_id = student_data["id"]
            student_name = student_data["name"]
            start_location = student_data.get("location", "classroom")
            
            # Create student with persona
            student = StudentAgent(student_name, self.memory, self.world, persona_id=student_id)
            student.move_to_location(start_location)
            self.student_agents.append(student)
            self.agents.append(student)
            
            # Create daily schedule for student using their preferences
            schedule = DailySchedule(student.name)
            self.daily_schedules[student.name] = schedule
    
    def create_daily_schedules(self, date: str):
        """Create daily schedules for all students with their preferences"""
        for student in self.student_agents:
            schedule = self.daily_schedules[student.name]
            # Get student preferences to pass to schedule creation
            agent_preferences = {
                "learning_goals": getattr(student, 'learning_goals', ["study", "improve skills"]),
                "preferred_locations": getattr(student, 'preferred_locations', ["library", "classroom"]),
                "social_preferences": getattr(student, 'social_preferences', ["collaborate", "network"]),
                "activity_preferences": getattr(student, 'activity_preferences', ["study", "practice", "discuss"])
            }
            # Create schedule with student's preferences
            schedule.create_daily_schedule(date, agent_preferences=agent_preferences)
    
    def run_simulation(self):
        """Run the entire simulation"""
        print(f"Starting simulation for {self.config['simulation_days']} days...")
        self.logger.log_event("simulation_start", f"Simulation started for {self.config['simulation_days']} days")
        
        # Initialize agents
        self.initialize_agents()
        
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
            schedule = self.daily_schedules[student.name]
            period_schedule = schedule.get_schedule_for_period(date, period)
            
            if period_schedule:
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


if __name__ == "__main__":
    sim_manager = SimulationManager()
    sim_manager.run_simulation()