import json
import random
from typing import Dict, List, Any, Tuple
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.memory_manager import MemoryManager


class WorldManager:
    def __init__(self, world_config_path: str, schedule_config_path: str):
        self.world_config = self.load_config(world_config_path)
        self.schedule_config = self.load_config(schedule_config_path)
        self.locations = self.world_config["locations"]
        self.agents = {}
        self.agent_positions = self.world_config.get("initial_positions", {})
        self.exam_questions = []
        self.exam_results = {}

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def register_agent(self, agent_name: str, agent: Any):
        """Register an agent in the world."""
        self.agents[agent_name] = agent
        if agent_name not in self.agent_positions:
            # Default to a random location if not specified
            self.agent_positions[agent_name] = random.choice(list(self.locations.keys()))

    def move_agent(self, agent_name: str, location: str) -> bool:
        """Move an agent to a specific location."""
        if location in self.locations:
            self.agent_positions[agent_name] = location
            agent = self.agents[agent_name]
            agent.set_location(location)
            return True
        return False

    def get_agents_at_location(self, location: str) -> List[str]:
        """Get list of agent names at a specific location."""
        return [name for name, pos in self.agent_positions.items() if pos == location]

    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get information about a location."""
        return self.locations.get(location, {})

    def get_current_world_state(self) -> Dict[str, Any]:
        """Get the current state of the world."""
        return {
            "locations": self.locations,
            "agent_positions": self.agent_positions,
            "time": getattr(self, 'current_day', 0),
            "period": getattr(self, 'current_time_period', '')
        }

    def print_world_state(self):
        """Print the current world state including agent positions."""
        print("\n" + "="*50)
        print("WORLD STATE")
        print("="*50)
        for agent_name, position in self.agent_positions.items():
            location_info = self.locations[position]
            print(f"{agent_name} is at {position} ({location_info['name']})")
        print("="*50)

    def get_mandatory_schedule(self, time_period: str, day: int = 0) -> Dict[str, str]:
        """Get the mandatory schedule for the current time period."""
        # Check if it's a weekend (simplified)
        is_weekend = day % 7 in [5, 6]  # Assuming day 0 is Monday
        
        if is_weekend and "weekends" in self.schedule_config["special_dates"]:
            return self.schedule_config["special_dates"]["weekends"][time_period]["mandatory"]
        else:
            return self.schedule_config["daily_schedule"][time_period]["mandatory"]

    def get_schedule_probability(self, time_period: str, day: int = 0) -> float:
        """Get the probability for following the schedule."""
        is_weekend = day % 7 in [5, 6]  # Assuming day 0 is Monday
        
        if is_weekend and "weekends" in self.schedule_config["special_dates"]:
            return self.schedule_config["special_dates"]["weekends"][time_period]["probability"]
        else:
            return self.schedule_config["daily_schedule"][time_period]["probability"]

    def generate_exam(self, knowledge_base_path: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """Generate an exam based on the knowledge base."""
        # Load knowledge base
        knowledge_base = []
        with open(knowledge_base_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    knowledge_base.append(json.loads(line.strip()))
        
        # Generate simple questions based on knowledge
        self.exam_questions = []
        for i in range(min(num_questions, len(knowledge_base))):
            knowledge_item = knowledge_base[i]
            question = f"What is {knowledge_item['topic']}?"
            answer = knowledge_item['content']
            
            exam_q = {
                "id": i + 1,
                "question": question,
                "answer": answer,
                "topic": knowledge_item['topic'],
                "difficulty": random.choice(["easy", "medium", "hard"])
            }
            self.exam_questions.append(exam_q)
        
        return self.exam_questions

    def conduct_exam(self, agents: List[Any]) -> Dict[str, float]:
        """Conduct an exam for all agents and return scores."""
        scores = {}
        
        for agent in agents:
            # Calculate score based on agent type and knowledge
            if hasattr(agent, 'is_expert') and agent.is_expert:
                # Expert agents have higher base knowledge
                base_score = 0.8
            else:
                # Student agents' score depends on what they've learned
                learned_content = []
                if hasattr(agent, 'knowledge_learned'):
                    learned_content = agent.knowledge_learned
                
                # Also check the agent's memories for learning-related content
                learning_memories = agent.memory_manager.search_memories(agent.name, "learning", limit=20)
                
                # Calculate score based on how much relevant content they've learned
                relevant_topics = set(q['topic'] for q in self.exam_questions)
                
                # Count learned topics from both direct knowledge and memories
                learned_topics = set()
                
                # From direct knowledge
                for content in learned_content:
                    for topic in relevant_topics:
                        if topic.lower() in content.lower():
                            learned_topics.add(topic)
                
                # From learning memories
                for memory in learning_memories:
                    for topic in relevant_topics:
                        if topic.lower() in memory['content'].lower():
                            learned_topics.add(topic)
                
                # Calculate base score based on percentage of topics learned
                base_score = len(learned_topics) / len(relevant_topics) if relevant_topics else 0.1
            
            # Add some randomness to the score, but ensure it's not negative
            score = min(1.0, max(0.0, base_score + random.uniform(-0.05, 0.1)))
            scores[agent.name] = round(score * 100, 2)
        
        self.exam_results = scores
        return scores

    def run_simulation(self, days: int, time_periods: List[str], max_dialogue_rounds: int):
        """Run the main simulation loop."""
        all_agents = list(self.agents.values())
        
        for day in range(days):
            self.current_day = day
            print(f"\n{'='*60}")
            print(f"DAY {day + 1}")
            print(f"{'='*60}")
            
            for period in time_periods:
                self.current_time_period = period
                print(f"\n--- {period.upper()} ---")
                
                # Print world state at the beginning of each period
                self.print_world_state()
                
                # Get mandatory schedule and probability
                mandatory_schedule = self.get_mandatory_schedule(period, day)
                probability = self.get_schedule_probability(period, day)
                
                # Each agent decides what to do based on schedule and personal preferences
                for agent in all_agents:
                    agent.set_day_and_time(day, period)
                    
                    # Create daily schedule based on mandatory schedule and personal preferences
                    activity = agent.create_daily_schedule(
                        {"probability": probability}, 
                        mandatory_schedule
                    )
                    
                    print(f"{agent.name} plans to: {activity}")
                    
                    # Find other agents at the same location
                    current_location = self.agent_positions[agent.name]
                    other_agents_at_location = [
                        self.agents[name] 
                        for name in self.get_agents_at_location(current_location) 
                        if name != agent.name
                    ]
                    
                    # Decide whether to initiate dialogue
                    if other_agents_at_location and random.random() < 0.5:
                        topic = random.choice(["studies", "schedule", "knowledge", "day's plan", "math concepts"])
                        print(f"{agent.name} initiates dialogue about '{topic}' with {len(other_agents_at_location)} other agent(s)")
                        dialogue_history = agent.initiate_dialogue(
                            other_agents_at_location, 
                            max_dialogue_rounds, 
                            topic
                        )
                    
                    # Add activity to memory
                    agent.generate_long_term_memory(f"During {period}, {activity}")
                    
                    # If it's a teaching period and there are students present
                    if agent.name == "teacher" and period in ["mid_morning"]:
                        # Teacher moves to classroom if not already there
                        if self.agent_positions[agent.name] != "classroom":
                            self.move_agent(agent.name, "classroom")
                            print(f"{agent.name} moved to classroom for teaching")
                        
                        # Find students in classroom
                        students_in_classroom = [
                            self.agents[name] 
                            for name in self.get_agents_at_location("classroom") 
                            if name != agent.name and isinstance(self.agents[name], StudentAgent)
                        ]
                        
                        if students_in_classroom:
                            # Teacher conducts a lesson
                            lesson_content = agent.teach(students_in_classroom, day + 1)
                            print(f"Teacher conducted lesson: {lesson_content}")
        
        return self.exam_results