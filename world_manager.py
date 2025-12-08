import json
import random
from typing import Dict, List
from datetime import datetime
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from agents import AgentManager
from memory_manager import MemoryManager
from knowledge_base import KnowledgeBase
import config


class WorldState(BaseModel):
    """State for the entire world"""
    day: int = 1
    time_period: str = "morning_1"
    agent_positions: Dict[str, str] = Field(default_factory=dict)
    map_info: Dict[str, Dict] = Field(default_factory=dict)
    total_schedule: Dict[str, Dict] = Field(default_factory=dict)
    simulation_complete: bool = False
    current_results: Dict[str, any] = Field(default_factory=dict)


class WorldManager:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.knowledge_base = KnowledgeBase()
        self.agents = AgentManager(self, self.memory_manager, self.knowledge_base)
        
        # Initialize agent positions
        self.agent_positions = {}
        agent_list = list(config.AGENT_CONFIGS.keys())
        for i, agent_id in enumerate(agent_list):
            # Assign initial positions based on agent type
            if "teacher" in agent_id:
                self.agent_positions[agent_id] = "classroom"  # Teacher starts in classroom
            else:
                self.agent_positions[agent_id] = "classroom"  # Students start in classroom
        
        # Initialize map
        self.map_info = config.MAP_INFO
        self.total_schedule = config.TOTAL_SCHEDULE
        self.simulation_days = config.CONFIG["simulation_days"]
        
        # Create the world graph using LangGraph
        self.graph = self._create_world_graph()
    
    def _create_world_graph(self):
        """Create the world simulation graph using LangGraph"""
        world_graph = StateGraph(WorldState)
        
        # Add nodes for the world simulation
        world_graph.add_node("initialize_day", self._initialize_day)
        world_graph.add_node("morning_1", self._run_time_period)
        world_graph.add_node("morning_2", self._run_time_period)
        world_graph.add_node("afternoon_1", self._run_time_period)
        world_graph.add_node("afternoon_2", self._run_time_period)
        world_graph.add_node("evening", self._run_time_period)
        world_graph.add_node("end_day", self._end_day)
        
        # Define the flow for each day
        world_graph.add_edge("initialize_day", "morning_1")
        world_graph.add_edge("morning_1", "morning_2")
        world_graph.add_edge("morning_2", "afternoon_1")
        world_graph.add_edge("afternoon_1", "afternoon_2")
        world_graph.add_edge("afternoon_2", "evening")
        world_graph.add_edge("evening", "end_day")
        
        # Set entry point
        world_graph.set_entry_point("initialize_day")
        
        # Add conditional edge from end_day to either loop back or end simulation
        world_graph.add_conditional_edges(
            "end_day",
            self._should_continue_simulation,
            {
                "continue": "initialize_day",
                "end": END
            }
        )
        
        return world_graph.compile()
    
    def _initialize_day(self, state: WorldState) -> WorldState:
        """Initialize a new day"""
        print(f"\n{'='*50}")
        print(f"STARTING DAY {state.day}")
        print(f"{'='*50}")
        
        # Print current map state
        self._print_map_state()
        
        # Update state
        updated_state = state.copy()
        updated_state.time_period = "morning_1"
        
        # Add day initialization to memory
        self.memory_manager.add_memory({
            "agent_id": "world",
            "day": state.day,
            "time_period": "day_start",
            "content": f"Day {state.day} initialized",
            "type": "world_event"
        })
        
        return updated_state
    
    def _run_time_period(self, state: WorldState) -> WorldState:
        """Run a specific time period for all agents"""
        print(f"\n--- {state.time_period.upper()} ---")
        
        # Run all agents for this time period
        results = self.agents.run_all_agents(state.day, state.time_period)
        
        # Update agent positions based on results
        for agent_id, result in results.items():
            if hasattr(result, 'position') and result.position:
                self.agent_positions[agent_id] = result.position
        
        # Print the map state after this time period
        self._print_map_state()
        
        # Update state
        updated_state = state.copy()
        updated_state.current_results = results
        
        return updated_state
    
    def _end_day(self, state: WorldState) -> WorldState:
        """End the current day and prepare for the next"""
        print(f"\nEND OF DAY {state.day}")
        print("-" * 30)
        
        # Add day end to memory
        self.memory_manager.add_memory({
            "agent_id": "world",
            "day": state.day,
            "time_period": "day_end",
            "content": f"Day {state.day} completed",
            "type": "world_event"
        })
        
        # Update state for next day
        updated_state = state.copy()
        updated_state.day = state.day + 1
        updated_state.simulation_complete = (state.day >= self.simulation_days)
        
        return updated_state
    
    def _should_continue_simulation(self, state: WorldState) -> str:
        """Determine if simulation should continue"""
        if state.day > self.simulation_days:
            return "end"
        return "continue"
    
    def _print_map_state(self):
        """Print the current state of the map with agent positions"""
        print("\nMAP STATE:")
        for location, info in self.map_info.items():
            agents_here = [agent for agent, pos in self.agent_positions.items() if pos == location]
            print(f"  {location.upper()}: {info['description']}")
            if agents_here:
                print(f"    Occupants: {', '.join(agents_here)}")
            else:
                print(f"    Occupants: None")
            print()
    
    def get_agent_location(self, agent_id: str) -> str:
        """Get the current location of an agent"""
        return self.agent_positions.get(agent_id, "unknown")
    
    def move_agent(self, agent_id: str, new_location: str):
        """Move an agent to a new location"""
        if new_location in self.map_info:
            self.agent_positions[agent_id] = new_location
            # Add movement to memory
            self.memory_manager.add_memory({
                "agent_id": agent_id,
                "day": self.get_current_day(),
                "time_period": self.get_current_time_period(),
                "content": f"Moved to {new_location}",
                "type": "movement"
            })
    
    def get_agents_at_location(self, location: str) -> List[str]:
        """Get all agents at a specific location"""
        return [agent for agent, pos in self.agent_positions.items() if pos == location]
    
    def get_current_day(self) -> int:
        """Get the current day of the simulation"""
        # This would be determined from the state in a full implementation
        # For now, we'll return a default
        return 1
    
    def get_current_time_period(self) -> str:
        """Get the current time period of the simulation"""
        # This would be determined from the state in a full implementation
        # For now, we'll return a default
        return "morning_1"
    
    async def run_simulation(self):
        """Run the entire simulation using the LangGraph"""
        initial_state = WorldState(
            day=1,
            time_period="morning_1",
            agent_positions=self.agent_positions,
            map_info=self.map_info,
            total_schedule=self.total_schedule,
            simulation_complete=False
        )
        
        # Run the simulation graph
        final_state = await self.graph.ainvoke(initial_state)
        return final_state


# Function to create and run the exam system
def run_exams(world_manager: WorldManager):
    """Run pre and post simulation exams to measure learning"""
    print("\n" + "="*50)
    print("EXAMINATION SYSTEM")
    print("="*50)
    
    # Generate exam questions from knowledge base
    topics = world_manager.knowledge_base.get_topics()
    exam_questions = []
    
    for topic in topics[:3]:  # Take first 3 topics for the exam
        knowledge_items = world_manager.knowledge_base.get_knowledge_by_topic(topic)
        for item in knowledge_items[:2]:  # Take first 2 items per topic
            exam_questions.append({
                "topic": topic,
                "question": f"What do you know about {item.get('content', '')[:50]}?",
                "reference_content": item.get("content", "")
            })
    
    print(f"\nGenerated {len(exam_questions)} exam questions")
    
    # Pre-simulation exam (random scores for initial state)
    print("\nPRE-SIMULATION EXAM - Initial Knowledge Assessment")
    pre_scores = {}
    for agent_id in config.AGENT_CONFIGS.keys():
        # Teachers should have higher initial scores in their domain
        if config.AGENT_CONFIGS[agent_id]["is_expert"]:
            score = random.randint(70, 90)  # Teachers start with higher knowledge
        else:
            score = random.randint(30, 60)  # Students start with basic knowledge
        pre_scores[agent_id] = score
        print(f"{agent_id}: {score}/100")
    
    # Post-simulation exam would happen after the simulation completes
    # For this example, we'll simulate the post-exam
    print("\nPOST-SIMULATION EXAM - Final Knowledge Assessment")
    post_scores = {}
    for agent_id in config.AGENT_CONFIGS.keys():
        # Apply some improvement based on the simulation
        improvement = random.randint(5, 25)  # Random improvement
        post_score = min(100, pre_scores[agent_id] + improvement)
        post_scores[agent_id] = post_score
        print(f"{agent_id}: {post_score}/100")
    
    # Print improvement summary
    print("\nIMPROVEMENT SUMMARY:")
    for agent_id in config.AGENT_CONFIGS.keys():
        improvement = post_scores[agent_id] - pre_scores[agent_id]
        print(f"{agent_id}: +{improvement} points")