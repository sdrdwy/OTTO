import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class WorldManager:
    def __init__(self):
        self.map_data = self._load_map()
        self.agent_locations = {}  # agent_name -> location
        self.location_agents = {}  # location -> [agent_names]
        self.current_date = datetime.now().date()
        self.day_count = 0
        
        # Initialize location_agents based on map
        for location in self.map_data['locations']:
            self.location_agents[location] = []
    
    def _load_map(self) -> Dict:
        """Load the map configuration"""
        with open('configs/map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def move_agent(self, agent_name: str, location: str) -> bool:
        """Move an agent to a specific location"""
        if location not in self.map_data['locations']:
            print(f"Location {location} does not exist in the map")
            return False
        
        # Remove agent from current location
        if agent_name in self.agent_locations:
            current_location = self.agent_locations[agent_name]
            if current_location in self.location_agents:
                if agent_name in self.location_agents[current_location]:
                    self.location_agents[current_location].remove(agent_name)
        
        # Add agent to new location
        self.agent_locations[agent_name] = location
        if location not in self.location_agents:
            self.location_agents[location] = []
        if agent_name not in self.location_agents[location]:
            self.location_agents[location].append(agent_name)
        
        return True
    
    def get_agent_location(self, agent_name: str) -> str:
        """Get the current location of an agent"""
        return self.agent_locations.get(agent_name, "unknown")
    
    def get_agents_at_location(self, location: str) -> List[str]:
        """Get all agents at a specific location"""
        return self.location_agents.get(location, [])
    
    def get_map_info(self) -> Dict:
        """Get information about the map"""
        return self.map_data
    
    def get_location_info(self, location: str) -> Dict:
        """Get information about a specific location"""
        return self.map_data['locations'].get(location, {})
    
    def advance_day(self) -> None:
        """Advance the simulation by one day"""
        self.day_count += 1
        self.current_date = self.current_date.replace(day=self.current_date.day + 1)
    
    def get_current_date(self) -> str:
        """Get the current date in the simulation"""
        return self.current_date.isoformat()
    
    def get_world_state(self) -> Dict:
        """Get the current state of the world"""
        return {
            "date": self.get_current_date(),
            "day_count": self.day_count,
            "agent_locations": self.agent_locations.copy(),
            "location_agents": {loc: agents[:] for loc, agents in self.location_agents.items()},
            "map_info": self.map_data
        }
    
    def print_world_state(self) -> None:
        """Print the current state of the world"""
        print(f"\n=== WORLD STATE - Day {self.day_count} ({self.get_current_date()}) ===")
        
        for location, agents in self.location_agents.items():
            if agents:  # Only show locations that have agents
                location_info = self.get_location_info(location)
                print(f"{location.upper()}: {location_info['name']}")
                print(f"  Description: {location_info['description']}")
                print(f"  Function: {location_info['function']}")
                print(f"  Agents present: {', '.join(agents) if agents else 'None'}")
                print()
    
    def is_special_day(self, date_str: str) -> Dict:
        """Check if the current date is a special day (holiday, weekend, etc.)"""
        # Load schedule config to check for special dates
        with open('configs/schedule.json', 'r', encoding='utf-8') as f:
            schedule_config = json.load(f)
        
        # Check if date is weekend (Saturday or Sunday)
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            weekday = date_obj.weekday()  # Monday is 0, Sunday is 6
            if weekday in [5, 6]:  # Saturday or Sunday
                return {"is_special": True, "type": "weekend", "name": "Weekend"}
        except:
            pass
        
        # Check if date is holiday
        holidays = schedule_config.get('special_dates', {}).get('holidays', [])
        for holiday in holidays:
            if holiday['date'] == date_str.split('T')[0]:  # Compare just the date part
                return {"is_special": True, "type": "holiday", "name": holiday['name']}
        
        return {"is_special": False, "type": "normal", "name": "Normal Day"}