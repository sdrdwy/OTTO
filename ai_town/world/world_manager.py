import json
from typing import Dict, List, Any
from ..configs.config_loader import ConfigLoader


class WorldManager:
    def __init__(self):
        # Load world configurations
        self.config = ConfigLoader.load_config('config')
        self.map_data = ConfigLoader.load_config('map')
        self.schedule_data = ConfigLoader.load_config('schedule')
        
        # Initialize agent positions (default to dormitory)
        self.agent_positions = {}
        self.agents = {}  # Will store agent instances
        
        # Initialize locations with agents present
        self.location_contents = {loc['name']: [] for loc in self.map_data['locations']}
    
    def register_agent(self, agent_name: str, agent_instance):
        """
        Register an agent in the world
        """
        self.agents[agent_name] = agent_instance
        self.agent_positions[agent_name] = "dormitory"  # Default starting position
        self.location_contents["dormitory"].append(agent_name)
    
    def move_agent(self, agent_name: str, destination: str) -> bool:
        """
        Move an agent to a specified location
        """
        if agent_name not in self.agents:
            return False
        
        # Remove agent from current location
        current_location = self.agent_positions[agent_name]
        if agent_name in self.location_contents[current_location]:
            self.location_contents[current_location].remove(agent_name)
        
        # Add agent to new location
        self.location_contents[destination].append(agent_name)
        self.agent_positions[agent_name] = destination
        
        return True
    
    def get_agents_at_location(self, location: str) -> List[str]:
        """
        Get list of agents at a specific location
        """
        return self.location_contents.get(location, [])
    
    def get_map_info(self) -> Dict[str, Any]:
        """
        Get information about the world map
        """
        return self.map_data
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """
        Get information about the daily schedule
        """
        return self.schedule_data
    
    def get_world_state(self) -> Dict[str, Any]:
        """
        Get the current state of the world
        """
        return {
            "agent_positions": self.agent_positions,
            "location_contents": self.location_contents,
            "map": self.map_data,
            "schedule": self.schedule_data
        }
    
    def display_map_status(self):
        """
        Display current status of the map with agent positions
        """
        print("\n" + "="*50)
        print("WORLD MAP STATUS")
        print("="*50)
        
        for location, agents in self.location_contents.items():
            location_info = next((loc for loc in self.map_data['locations'] if loc['name'] == location), {})
            print(f"\n📍 {location.upper()}")
            print(f"   Description: {location_info.get('description', 'N/A')}")
            print(f"   Function: {location_info.get('function', 'N/A')}")
            print(f"   Agents present: {agents if agents else 'None'}")
        
        print("="*50)