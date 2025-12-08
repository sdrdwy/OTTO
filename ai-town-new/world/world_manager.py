import json
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent


class WorldManager:
    def __init__(self, config_path: str = "configs/world/config.json"):
        # Load world configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Load map information
        map_path = self.config.get("map_file", "configs/world/map.json")
        with open(map_path, 'r', encoding='utf-8') as f:
            self.map_data = json.load(f)
        
        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {}
        self.locations: Dict[str, List[str]] = {}  # Maps location to list of agent names at that location
        
        # Initialize locations
        for location_id in self.map_data["locations"]:
            self.locations[location_id] = []
        
        # Load and initialize all agents
        self._initialize_agents()
        
        # Initialize exam
        self.exam_data = self._load_exam()
    
    def _initialize_agents(self):
        """Initialize all agents from their configuration files"""
        agent_configs = [
            "configs/agents/teacher.json",
            "configs/agents/student1.json", 
            "configs/agents/student2.json",
            "configs/agents/student3.json",
            "configs/agents/student4.json"
        ]
        
        for config_path in agent_configs:
            with open(config_path, 'r', encoding='utf-8') as f:
                agent_config = json.load(f)
            
            agent_id = agent_config["id"]
            agent_name = agent_config["name"]
            is_expert = agent_config.get("is_expert", False)
            
            if is_expert:
                # Create expert agent
                agent = ExpertAgent(
                    config_path=config_path,
                    knowledge_base_path=self.config.get("knowledge_base_file", "knowledge_base/knowledge.jsonl")
                )
                # Generate curriculum for the expert
                total_days = self.config.get("simulation_days", 10)
                agent.generate_curriculum(total_days)
            else:
                # Create student agent
                agent = StudentAgent(config_path=config_path)
            
            self.agents[agent_id] = agent
            # Add agent to their default location
            self.locations["dormitory"].append(agent_name)  # All agents start in dormitory
            agent.move_to_location("dormitory")
    
    def _load_exam(self) -> Dict[str, Any]:
        """Load the exam data"""
        exam_path = self.config.get("exam_file", "exams/exam.json")
        try:
            with open(exam_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Exam file not found: {exam_path}")
            return {"questions": []}
    
    def move_agent(self, agent_id: str, location: str) -> bool:
        """Move an agent to a specified location"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        old_location = agent.location
        
        # Remove agent from old location
        if agent.name in self.locations[old_location]:
            self.locations[old_location].remove(agent.name)
        
        # Add agent to new location
        if location in self.locations:
            self.locations[location].append(agent.name)
            agent.move_to_location(location)
            return True
        
        return False
    
    def get_agents_at_location(self, location: str) -> List[str]:
        """Get list of agent names at a specific location"""
        return self.locations.get(location, [])
    
    def get_map_info(self) -> Dict[str, Any]:
        """Return map information"""
        return self.map_data
    
    def get_agent_by_id(self, agent_id: str) -> BaseAgent:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agent_by_name(self, name: str) -> BaseAgent:
        """Get agent by name"""
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all agents"""
        return list(self.agents.values())
    
    def get_expert_agents(self) -> List[ExpertAgent]:
        """Get all expert agents"""
        return [agent for agent in self.agents.values() if isinstance(agent, ExpertAgent)]
    
    def get_student_agents(self) -> List[StudentAgent]:
        """Get all student agents"""
        return [agent for agent in self.agents.values() if isinstance(agent, StudentAgent)]
    
    def run_pre_simulation_exams(self) -> List[Dict[str, Any]]:
        """Run exams before the simulation starts"""
        results = []
        exam_questions = self.exam_data.get("questions", [])
        
        for agent in self.agents.values():
            if isinstance(agent, StudentAgent) or (isinstance(agent, ExpertAgent) and not agent.name.startswith("Professor")):
                result = agent.take_exam(exam_questions)
                results.append(result)
        
        return results
    
    def run_post_simulation_exams(self) -> List[Dict[str, Any]]:
        """Run exams after the simulation ends"""
        return self.run_pre_simulation_exams()  # Same process for post-simulation exams
    
    def print_map_status(self):
        """Print current map status showing agent locations"""
        print("\n=== MAP STATUS ===")
        for location, agents in self.locations.items():
            location_info = self.map_data["locations"][location]
            print(f"{location_info['name']} ({location}): {agents if agents else 'No agents present'}")
        print("==================\n")
    
    def process_time_period(self, period: str, date: str) -> List[Dict[str, Any]]:
        """Process a single time period for all agents"""
        period_events = []
        
        # Generate daily schedules for all agents
        for agent_id, agent in self.agents.items():
            # Get map info and other agents' memories for context
            map_info = self.get_map_info()
            other_memories = []
            
            # Get memories from other agents that might be relevant
            for other_agent_id, other_agent in self.agents.items():
                if other_agent_id != agent_id:
                    recent_memories = [mem.content for mem in other_agent.long_term_memory[-5:]]
                    other_memories.extend(recent_memories)
            
            # Generate schedule for this agent
            schedule = agent.generate_daily_schedule(date, map_info, other_memories)
            agent_schedule = schedule.get("schedule", {}).get(period, {})
            
            # Move agent according to their schedule
            target_location = agent_schedule.get("location", "dormitory")
            activity = agent_schedule.get("activity", "unspecified")
            
            # Move the agent
            self.move_agent(agent_id, target_location)
            
            # Record the movement
            event = {
                "agent": agent.name,
                "location": target_location,
                "activity": activity,
                "period": period,
                "date": date
            }
            period_events.append(event)
            
            # Add memory of this activity
            agent.add_memory(
                f"During {period} on {date}, I was at {target_location} doing {activity}",
                importance=0.5,
                metadata={"activity": activity, "location": target_location, "period": period}
            )
        
        # Check for possible interactions at each location
        for location, agent_names in self.locations.items():
            if len(agent_names) > 1:  # Multiple agents at the same location
                # Get the actual agent objects
                location_agents = [self.get_agent_by_name(name) for name in agent_names if self.get_agent_by_name(name)]
                
                if len(location_agents) > 1:
                    # Initiate dialogue between agents at the same location
                    max_rounds = self.config.get("max_dialogue_rounds", 5)
                    
                    # Select first agent to initiate dialogue
                    if location_agents:
                        initiating_agent = location_agents[0]
                        topic_options = ["course material", "study techniques", "recent activities", "upcoming plans"]
                        import random
                        topic = random.choice(topic_options)
                        
                        # Start dialogue
                        dialogue_history = initiating_agent.initiate_dialogue(
                            other_agents=location_agents[1:], 
                            topic=topic, 
                            max_rounds=max_rounds
                        )
                        
                        # Record dialogue event
                        dialogue_event = {
                            "type": "dialogue",
                            "location": location,
                            "participants": [agent.name for agent in location_agents],
                            "topic": topic,
                            "dialogue_history": dialogue_history
                        }
                        period_events.append(dialogue_event)
        
        return period_events