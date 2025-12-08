import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class WorldManager:
    def __init__(self, world_config_path: str = "config/world.json", 
                 schedule_config_path: str = "config/schedule.json"):
        self.world_config_path = world_config_path
        self.schedule_config_path = schedule_config_path
        self.map = {}
        self.agents_positions = {}
        self.schedule = {}
        self.current_day = 0
        self.current_period = ""
        
        self.load_world_config()
        self.load_schedule_config()
    
    def load_world_config(self):
        """Load world configuration including map and initial positions"""
        with open(self.world_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.map = config.get("map", {})
            self.agents_positions = config.get("initial_positions", {})
    
    def load_schedule_config(self):
        """Load schedule configuration"""
        with open(self.schedule_config_path, 'r', encoding='utf-8') as f:
            self.schedule = json.load(f)
    
    def get_location_info(self, location: str) -> Optional[Dict[str, str]]:
        """Get information about a specific location"""
        return self.map.get(location)
    
    def move_agent(self, agent_name: str, new_location: str) -> bool:
        """Move an agent to a new location"""
        if new_location in self.map:
            self.agents_positions[agent_name] = new_location
            return True
        return False
    
    def get_agents_at_location(self, location: str) -> List[str]:
        """Get all agents currently at a specific location"""
        agents = []
        for agent, pos in self.agents_positions.items():
            if pos == location:
                agents.append(agent)
        return agents
    
    def get_all_agents_positions(self) -> Dict[str, str]:
        """Get positions of all agents"""
        return self.agents_positions.copy()
    
    def get_current_schedule(self, day: int, period: str) -> Dict[str, Any]:
        """Get the schedule for a specific day and time period"""
        # Check for special dates first
        special_date_key = f"day_{day}"
        if special_date_key in self.schedule.get("special_dates", {}):
            if period in self.schedule["special_dates"][special_date_key]:
                return self.schedule["special_dates"][special_date_key][period]
        
        # Otherwise return default schedule
        return self.schedule["daily_schedule"].get(period, {
            "default": "free_time",
            "required": []
        })
    
    def display_map_state(self):
        """Display the current state of the map with agent positions"""
        print("\n" + "="*50)
        print("MAP STATE")
        print("="*50)
        
        for location, info in self.map.items():
            agents_here = self.get_agents_at_location(location)
            print(f"\n📍 {info['name']} ({location})")
            print(f"   Description: {info['description']}")
            print(f"   Purpose: {info['purpose']}")
            if agents_here:
                print(f"   Agents present: {', '.join(agents_here)}")
            else:
                print("   Agents present: None")
        
        print("="*50)
    
    def advance_day(self):
        """Advance the simulation to the next day"""
        self.current_day += 1
    
    def set_current_period(self, period: str):
        """Set the current time period"""
        self.current_period = period
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get the complete state of the world"""
        return {
            "day": self.current_day,
            "period": self.current_period,
            "map": self.map,
            "agent_positions": self.agents_positions
        }
    
    def reset_world(self):
        """Reset the world to initial state"""
        self.load_world_config()  # Reload initial positions
        self.current_day = 0
        self.current_period = ""