import json
import random
from typing import Dict, List, Any
from ..agents.teacher_agent import TeacherAgent
from ..agents.student_agent import StudentAgent
from ..configs.config_loader import ConfigLoader
from .world_manager import WorldManager


class SimulationEngine:
    def __init__(self):
        self.config = ConfigLoader.load_config('config')
        self.world_manager = WorldManager()
        self.total_days = self.config['total_days']
        self.max_rounds = self.config['max_round']
        self.exam_results = {}
        
        # Initialize agents
        self.agents = {}
        self.teacher = None
        self.students = []
        
        self._initialize_agents()
    
    def _initialize_agents(self):
        """
        Initialize all agents based on configuration files
        """
        # Create teacher
        self.teacher = TeacherAgent('teacher.json')
        self.agents[self.teacher.name] = self.teacher
        self.world_manager.register_agent(self.teacher.name, self.teacher)
        
        # Create students
        student_configs = ['student1.json', 'student2.json', 'student3.json', 'student4.json']
        for config_file in student_configs:
            student = StudentAgent(config_file)
            self.agents[student.name] = student
            self.students.append(student)
            self.world_manager.register_agent(student.name, student)
    
    def generate_initial_exam(self):
        """
        Generate an initial exam before the simulation starts
        """
        print("📝 Generating initial exam based on curriculum...")
        
        # Teacher generates exam questions
        exam_questions = self.teacher.generate_exam_questions()
        
        # Save exam to file
        with open('/workspace/ai_town/exams/initial_exam.json', 'w') as f:
            json.dump(exam_questions, f, indent=2)
        
        # Have all agents take the initial exam
        self.exam_results['initial'] = {}
        for agent_name, agent in self.agents.items():
            score = self._grade_exam_response(agent, exam_questions)
            self.exam_results['initial'][agent_name] = score
            print(f"   {agent_name} initial exam score: {score}/10")
    
    def generate_final_exam(self):
        """
        Generate a final exam after the simulation ends using the same questions
        """
        print("📝 Generating final exam...")
        
        # Load the same exam questions used initially
        try:
            with open('/workspace/ai_town/exams/initial_exam.json', 'r') as f:
                exam_questions = json.load(f)
        except FileNotFoundError:
            print("   Initial exam not found, using teacher to generate new exam...")
            exam_questions = self.teacher.generate_exam_questions()
        
        # Save final exam to file
        with open('/workspace/ai_town/exams/final_exam.json', 'w') as f:
            json.dump(exam_questions, f, indent=2)
        
        # Have all agents take the final exam
        self.exam_results['final'] = {}
        for agent_name, agent in self.agents.items():
            score = self._grade_exam_response(agent, exam_questions)
            self.exam_results['final'][agent_name] = score
            print(f"   {agent_name} final exam score: {score}/10")
    
    def _grade_exam_response(self, agent, exam_questions: List[Dict]) -> int:
        """
        Generate and grade an agent's response to exam questions
        """
        # For simplicity, we'll generate a score based on agent type and knowledge
        if isinstance(agent, TeacherAgent):
            # Teachers should score high on their own subject
            return min(10, 8 + random.randint(0, 2))
        else:
            # Students' scores may improve based on simulation participation
            base_score = random.randint(3, 7)
            # In a real implementation, this would be based on how much they learned
            return base_score
    
    def run_simulation(self):
        """
        Run the complete simulation for the specified number of days
        """
        print("🚀 Starting AI Town Simulation")
        print(f"   Total days: {self.total_days}")
        print(f"   Agents: {[name for name in self.agents.keys()]}")
        
        # Generate and take initial exam
        self.generate_initial_exam()
        
        # Run simulation day by day
        for day in range(1, self.total_days + 1):
            print(f"\n📅 DAY {day}")
            print("-" * 30)
            
            # Get world state for agents to use in schedule creation
            world_state = self.world_manager.get_world_state()
            
            # Each agent creates their daily schedule
            for agent_name, agent in self.agents.items():
                daily_schedule = agent.create_daily_schedule(day, self.total_days, world_state)
                print(f"   {agent_name} scheduled activities: {daily_schedule}")
            
            # Run through the day's time periods
            time_periods = self.config['simulation']['time_periods']
            for period in time_periods:
                print(f"\n   ⏰ {period.upper()}")
                
                # Display current map status
                self.world_manager.display_map_status()
                
                # Process each agent's activity for this time period
                for agent_name, agent in self.agents.items():
                    if agent_name in agent.daily_schedule and period in agent.daily_schedule:
                        activity = agent.daily_schedule[period]['activity']
                        location = agent.daily_schedule[period]['location']
                        
                        # Move agent to scheduled location
                        self.world_manager.move_agent(agent_name, location)
                        
                        # Process the scheduled activity
                        self._process_agent_activity(agent, activity, period, day)
        
        # After all days, run final exam
        self.generate_final_exam()
        
        # Print final results
        self._print_final_results()
    
    def _process_agent_activity(self, agent, activity: str, period: str, day: int):
        """
        Process an agent's scheduled activity
        """
        print(f"     🚶 {agent.name} moving to {agent.current_location}")
        
        if 'teach' in activity or 'class' in activity:
            if isinstance(agent, TeacherAgent):
                # Teacher conducts class
                students_at_location = [name for name, pos in self.world_manager.agent_positions.items() 
                                        if pos == agent.current_location and name != agent.name]
                
                if students_at_location:
                    lesson_content = agent.teach_class(students_at_location, day)
                    print(f"     👨‍🏫 {agent.name} teaching class: {lesson_content[:100]}...")
                    
                    # Students attend the class
                    for student_name in students_at_location:
                        student = self.agents[student_name]
                        if isinstance(student, StudentAgent):
                            student_response = student.attend_class(agent.name, lesson_content)
                            print(f"       👨‍🎓 {student_name} response: {student_response[:80]}...")
                else:
                    print(f"     👨‍🏫 {agent.name} preparing lessons (no students present)")
        
        elif 'study' in activity:
            # Agent studies independently
            topic = "mathematics"  # Could be more specific based on context
            study_result = agent.study_independently(topic)
            print(f"     📚 {agent.name} studying: {study_result[:100]}...")
        
        elif 'dialogue' in activity or 'social' in activity:
            # Initiate dialogue with other agents at the same location
            agents_at_location = self.world_manager.get_agents_at_location(agent.current_location)
            other_agents = [name for name in agents_at_location if name != agent.name]
            
            if other_agents:
                topic = "general discussion"  # Could be more specific
                dialogue_history = agent.initiate_dialogue(other_agents, topic, self.max_rounds)
                print(f"     💬 {agent.name} participated in dialogue with {other_agents}")
            else:
                print(f"     🤐 {agent.name} had no one to talk to at {agent.current_location}")
        
        elif 'rest' in activity:
            print(f"     😴 {agent.name} resting at {agent.current_location}")
        
        else:
            print(f"     🔄 {agent.name} doing {activity} at {agent.current_location}")
    
    def _print_final_results(self):
        """
        Print the final exam results comparing initial and final scores
        """
        print("\n" + "="*60)
        print("📊 FINAL SIMULATION RESULTS")
        print("="*60)
        
        print("\nInitial vs Final Exam Scores:")
        print("-" * 40)
        for agent_name in self.agents.keys():
            initial_score = self.exam_results['initial'].get(agent_name, 0)
            final_score = self.exam_results['final'].get(agent_name, 0)
            improvement = final_score - initial_score
            print(f"{agent_name:12} | Initial: {initial_score:2d} | Final: {final_score:2d} | Change: {improvement:+3d}")
        
        print("\nThank you for running the AI Town Simulation!")
        print("="*60)