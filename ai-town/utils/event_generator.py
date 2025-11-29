"""
Event Generator for AI Town
Manages random events and festivals that occur periodically
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os


class EventGenerator:
    def __init__(self, world_config_file: str = "config/world_config.json"):
        self.world_config_file = world_config_file
        self.world_config = self.load_world_config()
        
        # Define festival types and activities
        self.festival_types = [
            "Science Fair", "Art Exhibition", "Math Competition", "Literature Festival",
            "Music Festival", "Sports Day", "Cultural Festival", "Technology Showcase",
            "Debate Competition", "Book Reading Event", "Science Olympiad", "Creative Workshop"
        ]
        
        # Define festival activities
        self.festival_activities = [
            "participate in competitions", "showcase talents", "learn new skills",
            "network with others", "engage in discussions", "collaborate on projects",
            "share knowledge", "celebrate achievements", "explore creative ideas"
        ]
        
        # Track last festival date
        self.last_festival_date = None
    
    def load_world_config(self) -> Dict[str, Any]:
        """Load world configuration from file"""
        if os.path.exists(self.world_config_file):
            try:
                with open(self.world_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading world config: {e}")
        
        # Default configuration
        return {
            "simulation_days": 30,
            "event_frequency": 14,  # Every 14 days
            "current_day": 0
        }
    
    def save_world_config(self):
        """Save world configuration to file"""
        try:
            with open(self.world_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.world_config, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving world config: {e}")
    
    def increment_day(self):
        """Increment the current day in the simulation"""
        self.world_config["current_day"] += 1
        self.save_world_config()
    
    def should_generate_festival(self) -> bool:
        """Check if it's time to generate a festival based on frequency"""
        current_day = self.world_config.get("current_day", 0)
        event_frequency = self.world_config.get("event_frequency", 14)
        
        # Check if we've reached a multiple of the event frequency
        if current_day > 0 and current_day % event_frequency == 0:
            return True
        return False
    
    def generate_festival(self) -> Dict[str, Any]:
        """Generate a random festival event"""
        festival_type = random.choice(self.festival_types)
        activities = random.sample(self.festival_activities, k=random.randint(2, 4))
        
        festival = {
            "type": festival_type,
            "activities": activities,
            "location": random.choice(["classroom", "park", "cafe", "lab", "library"]),
            "duration_hours": random.randint(4, 8),
            "participants": [],
            "description": f"A {festival_type.lower()} featuring {', '.join(activities[:2])}",
            "date": datetime.now().isoformat()
        }
        
        # Update last festival date
        self.last_festival_date = datetime.now()
        
        return festival
    
    def generate_random_event(self) -> Dict[str, Any]:
        """Generate a random non-festival event"""
        event_types = [
            "Study Group", "Research Session", "Group Discussion", "Peer Review",
            "Collaboration Session", "Knowledge Sharing", "Problem Solving Session"
        ]
        
        event_type = random.choice(event_types)
        location = random.choice(["classroom", "library", "lab", "cafe", "park"])
        
        event = {
            "type": event_type,
            "location": location,
            "duration_hours": random.randint(1, 3),
            "participants": [],
            "description": f"A {event_type.lower()} session at {location}",
            "date": datetime.now().isoformat()
        }
        
        return event
    
    def get_next_festival_day(self) -> int:
        """Get the day number for the next festival"""
        current_day = self.world_config.get("current_day", 0)
        event_frequency = self.world_config.get("event_frequency", 14)
        
        # Calculate next festival day
        next_festival_day = ((current_day // event_frequency) + 1) * event_frequency
        return next_festival_day
    
    def get_days_until_next_festival(self) -> int:
        """Get number of days until next festival"""
        current_day = self.world_config.get("current_day", 0)
        event_frequency = self.world_config.get("event_frequency", 14)
        
        next_festival_day = ((current_day // event_frequency) + 1) * event_frequency
        return next_festival_day - current_day


class FestivalManager:
    def __init__(self, event_generator: EventGenerator):
        self.event_generator = event_generator
        self.active_festivals = []
        self.past_festivals = []
    
    def check_and_generate_festival(self) -> Dict[str, Any]:
        """Check if we should generate a festival and generate if needed"""
        if self.event_generator.should_generate_festival():
            festival = self.event_generator.generate_festival()
            self.active_festivals.append(festival)
            return festival
        return None
    
    def add_participants_to_festival(self, festival_idx: int, participants: List[str]):
        """Add participants to a festival"""
        if 0 <= festival_idx < len(self.active_festivals):
            self.active_festivals[festival_idx]["participants"] = participants
    
    def end_active_festivals(self):
        """Move active festivals to past festivals"""
        for festival in self.active_festivals:
            self.past_festivals.append(festival)
        self.active_festivals = []
    
    def get_active_festivals(self) -> List[Dict[str, Any]]:
        """Get all active festivals"""
        return self.active_festivals
    
    def get_past_festivals(self) -> List[Dict[str, Any]]:
        """Get all past festivals"""
        return self.past_festivals