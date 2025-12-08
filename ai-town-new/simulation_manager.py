import json
from datetime import datetime
from typing import List, Dict, Any
from agents import TeacherAgent, StudentAgent
from world import WorldManager
from memory.knowledge_base import KnowledgeBase


class SimulationManager:
    def __init__(self):
        # Load configuration
        with open('configs/config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Initialize world
        self.world_manager = WorldManager()
        
        # Initialize agents
        self.agents = {}
        self.teacher = None
        self.students = []
        
        # Initialize knowledge base for exam generation
        self.knowledge_base = KnowledgeBase("mathematics")
        
        # Initialize exam data
        self.exam_data = None
    
    def initialize_agents(self):
        """Initialize all agents from their configuration files"""
        # Initialize teacher
        self.teacher = TeacherAgent('configs/teacher_config.json')
        self.agents[self.teacher.name] = self.teacher
        
        # Initialize students
        student_configs = [
            'configs/student1_config.json',
            'configs/student2_config.json', 
            'configs/student3_config.json',
            'configs/student4_config.json'
        ]
        
        for config_path in student_configs:
            student = StudentAgent(config_path)
            self.students.append(student)
            self.agents[student.name] = student
        
        # Place all agents in their initial locations
        for agent in [self.teacher] + self.students:
            self.world_manager.move_agent(agent.name, agent.location)
    
    def generate_exam(self):
        """Generate an exam based on the knowledge base"""
        # Load exam template
        with open('exams/exam_template.json', 'r', encoding='utf-8') as f:
            self.exam_data = json.load(f)
        
        print("Exam generated for pre-simulation and post-simulation assessment")
    
    def run_pre_simulation_exam(self):
        """Run exam before simulation starts"""
        print("\n=== PRE-SIMULATION EXAM ===")
        for student in self.students:
            result = student.take_exam(self.exam_data)
            print(f"{student.name} pre-simulation exam result: {result['percentage']:.1f}% ({result['grade']})")
    
    def run_post_simulation_exam(self):
        """Run exam after simulation completes"""
        print("\n=== POST-SIMULATION EXAM ===")
        for student in self.students:
            result = student.take_exam(self.exam_data)
            print(f"{student.name} post-simulation exam result: {result['percentage']:.1f}% ({result['grade']})")
            
            # Compare with pre-simulation score if available
            pre_result = student.exam_scores.get(f"pre_{self.exam_data['exam_id']}")
            if pre_result:
                improvement = result['percentage'] - pre_result['percentage']
                print(f"  Improvement: {improvement:+.1f}%")
    
    def run_simulation(self):
        """Run the complete simulation"""
        print("Initializing AI Town Simulation...")
        
        # Initialize agents
        self.initialize_agents()
        
        # Generate exam
        self.generate_exam()
        
        # Run pre-simulation exam
        self.run_pre_simulation_exam()
        
        # Get total days to simulate
        total_days = self.config['days_to_simulate']
        
        # Generate curriculum for teacher
        curriculum = self.teacher.generate_curriculum(total_days)
        print(f"\nGenerated curriculum for {total_days} days")
        
        # Main simulation loop
        for day in range(total_days):
            print(f"\n{'='*50}")
            print(f"DAY {day + 1}")
            print(f"{'='*50}")
            
            # Advance world day
            self.world_manager.advance_day()
            current_date = self.world_manager.get_current_date()
            
            # Print world state at the beginning of each day
            self.world_manager.print_world_state()
            
            # Check if special day
            special_day_info = self.world_manager.is_special_day(current_date)
            if special_day_info['is_special']:
                print(f"Special day: {special_day_info['name']} ({special_day_info['type']})")
            
            # Each agent generates their daily schedule
            all_agents = [self.teacher] + self.students
            agent_schedules = {}
            
            for agent in all_agents:
                # Get agent's previous memories to inform schedule
                previous_memories = agent.memory.get_recent_memories(limit=10)
                
                # Generate daily schedule
                schedule = agent.generate_daily_schedule(
                    current_date, 
                    self.world_manager.get_map_info(), 
                    previous_memories
                )
                agent_schedules[agent.name] = schedule
                
                print(f"\n{agent.name}'s schedule for {current_date}:")
                for period, activity in schedule.items():
                    print(f"  {period}: {activity['activity']} at {activity['location']}")
            
            # Process each time period
            for period in self.config['time_periods']:
                print(f"\n--- {period.upper()} ---")
                
                # Agents execute their scheduled activities
                for agent in all_agents:
                    if period in agent_schedules[agent.name]:
                        scheduled_activity = agent_schedules[agent.name][period]
                        activity = scheduled_activity['activity']
                        location = scheduled_activity['location']
                        
                        # Move agent to scheduled location
                        agent.move_to_location(location)
                        
                        # Perform activity based on type
                        if 'teaching' in activity and agent == self.teacher:
                            # Teacher teaches - find students at same location
                            local_students = [s for s in self.students 
                                            if self.world_manager.get_agent_location(s.name) == location]
                            if local_students:
                                student_names = [s.name for s in local_students]
                                topic = scheduled_activity.get('topic', 'General Mathematics')
                                print(f"{agent.name} is teaching {topic} to {', '.join(student_names)}")
                                
                                # Teacher teaches each student
                                for student in local_students:
                                    teaching_result = self.teacher.teach_student(student.name, topic)
                                    print(f"  {student.name} learned: {teaching_result[:100]}...")
                                    
                                    # Student processes the learning
                                    student.study_topic(topic)
                        
                        elif 'study' in activity or 'review' in activity:
                            # Student studies
                            if agent in self.students:
                                print(f"{agent.name} is studying: {activity}")
                                agent.study_topic(activity)
                        
                        elif 'class' in activity or 'attend' in activity:
                            # Attending class
                            print(f"{agent.name} is attending class: {activity}")
                        
                        else:
                            # Other activities
                            print(f"{agent.name} is doing: {activity} at {location}")
                        
                        # Generate memory for the activity
                        agent.generate_memory(f"Completed {activity} at {location} during {period}", "daily_activity")
                
                # Check for opportunities for conversations or battles
                locations_with_agents = {}
                for agent in all_agents:
                    loc = self.world_manager.get_agent_location(agent.name)
                    if loc not in locations_with_agents:
                        locations_with_agents[loc] = []
                    locations_with_agents[loc].append(agent)
                
                # Process locations with multiple agents
                for location, agents_at_location in locations_with_agents.items():
                    if len(agents_at_location) > 1:
                        # Agents at same location can interact
                        print(f"\nInteractions at {location}:")
                        
                        # Try to initiate conversations
                        for agent in agents_at_location:
                            other_agents = [a for a in agents_at_location if a != agent]
                            if other_agents and len(other_agents) > 0:
                                # Select a random other agent to start conversation with
                                conversation_partner = other_agents[0]
                                
                                # Check if both agents want to participate
                                if agent.participate_in_conversation({
                                    'topic': 'general chat',
                                    'participants': [agent.name, conversation_partner.name],
                                    'location': location
                                }) and conversation_partner.participate_in_conversation({
                                    'topic': 'general chat',
                                    'participants': [agent.name, conversation_partner.name],
                                    'location': location
                                }):
                                    print(f"  {agent.name} and {conversation_partner.name} start a conversation")
                                    
                                    # Simple conversation for now
                                    conversation_result = agent.initiate_conversation(
                                        [conversation_partner.name], 
                                        "general chat", 
                                        self.config['max_round']
                                    )
                                    print(f"    Conversation completed with {len(conversation_result)} exchanges")
                
                # Small chance of battles happening
                import random
                if random.random() < 0.1:  # 10% chance of a battle
                    if len(all_agents) >= 2:
                        # Randomly select two agents for a battle
                        import random
                        battle_participants = random.sample(all_agents, 2)
                        agent1, agent2 = battle_participants[0], battle_participants[1]
                        
                        if (self.world_manager.get_agent_location(agent1.name) == 
                            self.world_manager.get_agent_location(agent2.name)):
                            print(f"\nBattle between {agent1.name} and {agent2.name}!")
                            battle_result = agent1.battle(agent2.name)
                            print(f"  {battle_result['winner']} won the battle!")
        
        # Run post-simulation exam
        self.run_post_simulation_exam()
        
        # Print final summary
        print(f"\n{'='*50}")
        print("SIMULATION COMPLETED")
        print(f"{'='*50}")
        
        print("\nFinal exam score changes:")
        for student in self.students:
            pre_result = student.exam_scores.get(f"pre_{self.exam_data['exam_id']}")
            post_result = student.exam_scores.get(f"post_{self.exam_data['exam_id']}")
            if pre_result and post_result:
                improvement = post_result['percentage'] - pre_result['percentage']
                print(f"{student.name}: {pre_result['percentage']:.1f}% → {post_result['percentage']:.1f}% ({improvement:+.1f}%)")
        
        print(f"\nSimulation ran for {total_days} days with {len(all_agents)} agents.")
        print("Agents' final locations:")
        for agent in all_agents:
            location = self.world_manager.get_agent_location(agent.name)
            print(f"  {agent.name}: {location}")