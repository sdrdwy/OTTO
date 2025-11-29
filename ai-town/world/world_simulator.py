"""
World Simulator
Creates a simple text-based world with locations, events and a calendar system
"""
import random
from typing import List, Dict
from utils.calendar import Calendar


class WorldSimulator:
    def __init__(self):
        self.locations = {
            "library": {
                "description": "A quiet place filled with books and knowledge",
                "agents": [],
                "events": ["study session", "book discussion", "research"]
            },
            "classroom": {
                "description": "A place for learning and discussions",
                "agents": [],
                "events": ["lecture", "group discussion", "presentation"]
            },
            "park": {
                "description": "A peaceful outdoor area for relaxation and casual conversations",
                "agents": [],
                "events": ["casual chat", "reflection", "nature observation"]
            },
            "cafe": {
                "description": "A cozy place for informal meetings and conversations",
                "agents": [],
                "events": ["coffee chat", "debate", "idea sharing"]
            },
            "lab": {
                "description": "A place for experiments and scientific discussions",
                "agents": [],
                "events": ["experiment", "hypothesis discussion", "data analysis"]
            }
        }
        
        self.world_events = [
            "sunny day", "rainy day", "festival", "conference", "workshop"
        ]
        
        self.current_world_event = random.choice(self.world_events)
        
        # Initialize calendar system
        self.calendar = Calendar()
    
    def get_map(self) -> str:
        """
        Return a text-based map of the world
        """
        map_str = "AI Town Map:\n"
        map_str += "=============\n"
        
        for location, details in self.locations.items():
            agent_names = [agent.name for agent in details["agents"]]
            map_str += f"{location.capitalize()}: {details['description']}\n"
            if agent_names:
                map_str += f"  Occupants: {', '.join(agent_names)}\n"
            else:
                map_str += "  Occupants: None\n"
            map_str += "\n"
        
        map_str += f"Current World Event: {self.current_world_event}\n"
        return map_str
    
    def move_agent(self, agent, from_location: str, to_location: str):
        """
        Move an agent from one location to another
        """
        if from_location in self.locations and agent in self.locations[from_location]["agents"]:
            self.locations[from_location]["agents"].remove(agent)
        
        if to_location in self.locations and agent not in self.locations[to_location]["agents"]:
            self.locations[to_location]["agents"].append(agent)
    
    def add_agent_to_location(self, agent, location: str):
        """
        Add an agent to a specific location
        """
        if location in self.locations:
            if agent not in self.locations[location]["agents"]:
                self.locations[location]["agents"].append(agent)
    
    def remove_agent_from_location(self, agent, location: str):
        """
        Remove an agent from a specific location
        """
        if location in self.locations and agent in self.locations[location]["agents"]:
            self.locations[location]["agents"].remove(agent)
    
    def get_agents_at_location(self, location: str) -> List:
        """
        Get all agents at a specific location
        """
        if location in self.locations:
            return self.locations[location]["agents"]
        return []
    
    def get_random_location(self) -> str:
        """
        Get a random location
        """
        return random.choice(list(self.locations.keys()))
    
    def trigger_random_event(self) -> str:
        """
        Trigger a random event at a random location
        """
        location = random.choice(list(self.locations.keys()))
        event = random.choice(self.locations[location]["events"])
        
        event_description = f"Event: {event} happening at {location}"
        return event_description
    
    def get_location_description(self, location: str) -> str:
        """
        Get description of a location
        """
        if location in self.locations:
            return self.locations[location]["description"]
        return "Unknown location"
    
    def update_world_event(self):
        """
        Update the current world event
        """
        self.current_world_event = random.choice(self.world_events)
    
    def schedule_event(self, agent_name: str, title: str, start_time, end_time, description: str = "", location: str = ""):
        """
        Schedule an event in the calendar
        """
        return self.calendar.schedule_event(agent_name, title, start_time, end_time, description, location)
    
    def get_upcoming_events(self, agent_name: str, hours: int = 24):
        """
        Get upcoming events for an agent
        """
        return self.calendar.get_upcoming_events(agent_name, hours)
    
    def get_calendar_summary(self, agent_name: str):
        """
        Get calendar summary for an agent
        """
        return self.calendar.get_calendar_summary(agent_name)
    
    def schedule_meeting(self, participants: List[str], title: str, start_time, end_time, description: str = "", location: str = ""):
        """
        Schedule a meeting between multiple agents
        """
        return self.calendar.schedule_meeting(participants, title, start_time, end_time, description, location)