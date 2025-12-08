import json
from typing import Dict, List, Any
from datetime import datetime
from world.calendar import Calendar


class WorldSimulator:
    def __init__(self, map_config_path: str = "./config/map.json", system_config_path: str = "./config/system.json"):
        with open(system_config_path, 'r') as f:
            self.system_config = json.load(f)
        
        with open(map_config_path, 'r') as f:
            self.map = json.load(f)
        
        self.agents = {}
        self.calendar = Calendar()
        self.current_day = 0
        self.current_time_slot_idx = 0
        self.time_slots = self.system_config['simulation']['time_slots']
        self.exam_questions = []
        self.exam_scores = {}
        self.total_days = self.system_config['simulation']['total_days']
        
        # Initialize agent positions in the map
        for location in self.map['locations'].values():
            location['agents'] = []

    def register_agent(self, agent):
        """Register an agent with the world"""
        self.agents[agent.name] = agent
        # Place agent at a default location initially
        if self.map['locations']:
            default_location = list(self.map['locations'].keys())[0]
            agent.set_location(default_location)
            self.map['locations'][default_location]['agents'].append(agent.name)

    def move_agent(self, agent_name: str, location: str) -> bool:
        """Move an agent to a specific location"""
        if agent_name not in self.agents:
            return False
        
        agent = self.agents[agent_name]
        current_location = agent.get_current_location()
        
        # Remove agent from current location
        if current_location and current_location in self.map['locations']:
            if agent_name in self.map['locations'][current_location]['agents']:
                self.map['locations'][current_location]['agents'].remove(agent_name)
        
        # Add agent to new location
        if location in self.map['locations']:
            self.map['locations'][location]['agents'].append(agent_name)
            agent.set_location(location)
            return True
        
        return False

    def get_agents_at_location(self, location: str) -> List[str]:
        """Get list of agent names at a specific location"""
        if location in self.map['locations']:
            return self.map['locations'][location]['agents'][:]
        return []

    def get_agent_by_name(self, name: str):
        """Get agent object by name"""
        return self.agents.get(name)

    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get information about a specific location"""
        return self.map['locations'].get(location, {})

    def display_world_state(self):
        """Display current world state including agent positions and locations"""
        print(f"\n=== 日期: {self.calendar.get_current_date_str()} ===")
        print("地图状态:")
        for loc_name, loc_info in self.map['locations'].items():
            agents_here = loc_info['agents']
            print(f"  {loc_name}: {loc_info['description']} | 人员: {agents_here}")
        print()

    def start_simulation(self, agents_list):
        """Start the world simulation"""
        print("开始模拟世界运行...")
        
        # Register all agents
        for agent in agents_list:
            self.register_agent(agent)
        
        # Generate exam before simulation starts
        expert_agent = None
        for agent in agents_list:
            if hasattr(agent, 'is_expert') and agent.is_expert:
                expert_agent = agent
                break
        
        if expert_agent:
            num_questions = self.system_config['simulation']['exam_question_count']
            self.exam_questions = expert_agent.create_exam(num_questions)
            print(f"已生成考试题目 ({len(self.exam_questions)}题)")
            
            # Pre-simulation exam
            print("\n=== 模拟开始前考试 ===")
            for agent_name, agent in self.agents.items():
                if not agent.is_expert:  # Only students take the exam
                    answers = agent.take_exam(self.exam_questions)
                    scores = expert_agent.grade_exam(agent_name, answers, self.exam_questions)
                    self.exam_scores[f"{agent_name}_pre"] = scores['total_score']
                    print(f"{agent_name} 考试成绩: {scores['total_score']:.1f}")
        
        # Run simulation for specified number of days
        for day in range(self.total_days):
            print(f"\n{'='*50}")
            print(f"第 {day+1} 天开始")
            print(f"{'='*50}")
            
            # Advance calendar to next day
            self.calendar.advance_day()
            
            # Display world state at the beginning of each day
            self.display_world_state()
            
            # Each day has multiple time slots
            for time_slot_idx, time_slot in enumerate(self.time_slots):
                print(f"\n--- 时间段: {time_slot} ---")
                
                # Get the global schedule for this time slot
                day_schedule = self.calendar.get_schedule_for_day()
                time_slot_schedule = day_schedule.get(time_slot, {})
                
                # Each agent creates their daily schedule and acts accordingly
                for agent_name, agent in self.agents.items():
                    # Create daily schedule based on global schedule, map info, and personal memories
                    personal_memories = agent.long_term_memory.search_memories(limit=5)
                    agent.create_daily_schedule(
                        date=self.calendar.get_current_date_str(),
                        world_map=self.map,
                        global_schedule=time_slot_schedule,
                        personal_memories=personal_memories
                    )
                    
                    # Get the action for this time slot
                    action = agent.get_action_for_time_slot(time_slot)
                    
                    # Move agent to designated location if different from current
                    if action['location'] != agent.get_current_location():
                        self.move_agent(agent_name, action['location'])
                    
                    print(f"{agent_name} 在 {action['location']} 进行 {action['activity']} (原因: {action['reason']})")
                    
                    # Generate memory of the activity
                    activity_memory = {
                        "type": "daily_activity",
                        "timestamp": str(datetime.now()),
                        "location": action['location'],
                        "activity": action['activity'],
                        "reason": action['reason'],
                        "summary": f"{agent_name}在{action['location']}进行了{action['activity']}"
                    }
                    agent.generate_memory(activity_memory)
                
                # Handle interactions between agents at the same location
                self.handle_interactions(time_slot)
                
                # Process any requests from agents
                self.process_agent_requests()
        
        # Post-simulation exam
        print(f"\n{'='*50}")
        print("模拟结束后考试")
        print(f"{'='*50}")
        
        if expert_agent:
            print("\n=== 模拟结束后考试 ===")
            for agent_name, agent in self.agents.items():
                if not agent.is_expert:  # Only students take the exam
                    answers = agent.take_exam(self.exam_questions)
                    scores = expert_agent.grade_exam(agent_name, answers, self.exam_questions)
                    self.exam_scores[f"{agent_name}_post"] = scores['total_score']
                    print(f"{agent_name} 考试成绩: {scores['total_score']:.1f}")
        
        # Print final results
        print(f"\n{'='*50}")
        print("最终成绩对比")
        print(f"{'='*50}")
        for agent_name in [name for name in self.agents.keys() if not self.agents[name].is_expert]:
            pre_score = self.exam_scores.get(f"{agent_name}_pre", 0)
            post_score = self.exam_scores.get(f"{agent_name}_post", 0)
            improvement = post_score - pre_score
            print(f"{agent_name}: {pre_score:.1f} -> {post_score:.1f} (提升: {improvement:+.1f})")

    def handle_interactions(self, time_slot: str):
        """Handle interactions between agents at the same location"""
        # Group agents by location
        agents_by_location = {}
        for agent_name, agent in self.agents.items():
            location = agent.get_current_location()
            if location not in agents_by_location:
                agents_by_location[location] = []
            agents_by_location[location].append(agent_name)
        
        # Process interactions at each location
        for location, agent_names in agents_by_location.items():
            if len(agent_names) > 1:
                # Multiple agents at the same location - potentially start dialogues or battles
                print(f"  在 {location} 有 {len(agent_names)} 个代理: {agent_names}")
                
                # Randomly decide if they interact (for now)
                import random
                if random.random() > 0.3:  # 70% chance of interaction
                    # Start a multi-agent dialogue
                    max_rounds = self.system_config['simulation']['max_dialogue_rounds']
                    
                    # Select a random topic for the dialogue
                    topics = ["学习交流", "日常聊天", "学术讨论", "兴趣分享"]
                    topic = random.choice(topics)
                    
                    print(f"    开始关于 '{topic}' 的多轮对话...")
                    
                    # Have the first agent initiate the dialogue
                    initiating_agent = self.agents[agent_names[0]]
                    dialogue_history = initiating_agent.initiate_dialogue(
                        participants=agent_names[1:],  # Others participate
                        topic=topic,
                        max_rounds=max_rounds,
                        world_simulator=self
                    )
                    
                    if dialogue_history:
                        print(f"    对话结束，共 {len(dialogue_history)} 轮")

    def process_agent_requests(self):
        """Process any requests from agents (like battles, etc.)"""
        # This method can be extended to handle various types of agent requests
        pass
