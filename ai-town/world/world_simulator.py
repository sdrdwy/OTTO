"""
World Simulator
Creates a simple text-based world with locations, events and a calendar system
"""
import random
import json
from typing import List, Dict
from utils.calendar import Calendar


class WorldSimulator:
    def __init__(self, map_config_path="world/map_config.json"):
        # Load map configuration from JSON file
        with open(map_config_path, 'r', encoding='utf-8') as f:
            map_config = json.load(f)
        
        self.locations = map_config["locations"]
        self.world_events = map_config["world_events"]
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
    
    def trigger_class_event(self, teacher_agent, student_agents: List, subject: str = "General Class"):
        """
        Trigger a class event in the classroom with teacher and students
        """
        classroom = "classroom"
        
        # Ensure all participants are in the classroom
        self.add_agent_to_location(teacher_agent, classroom)
        teacher_agent.location = classroom
        
        for student in student_agents:
            self.add_agent_to_location(student, classroom)
            student.location = classroom
        
        event_description = f"Class Event: {subject} class with {teacher_agent.name} and students {[s.name for s in student_agents]} in {classroom}"
        print(event_description)
        
        # Conduct the class interaction
        teacher_agent.interact_with_students(student_agents)
        
        return event_description
    
    def trigger_event_at_location(self, location: str, event_type: str, participants: List, topic: str = None):
        """
        Trigger a specific event at a location with specific participants
        """
        if location not in self.locations:
            return f"Location {location} does not exist"
        
        # Move all participants to the location
        for agent in participants:
            self.add_agent_to_location(agent, location)
            agent.location = location
        
        event_description = f"Event: {event_type} at {location} with {[p.name for p in participants]}"
        print(event_description)
        
        # Different event types have different interaction patterns
        if event_type.lower() in ["discussion", "debate", "group work"]:
            # Group interaction
            if participants and hasattr(participants[0], 'interact'):
                participants[0].interact(participants[1:], topic or event_type)
        elif event_type.lower() == "festival":
            # Festival-specific interaction
            for agent in participants:
                if hasattr(agent, 'interact'):
                    agent.interact(participants, topic or "festival activities")
        
        return event_description
    
    def check_location_interactions(self):
        """
        Check for agents in the same location and trigger interactions based on personalities and memory
        """
        interactions = []
        
        for location, details in self.locations.items():
            agents_at_location = details["agents"]
            
            if len(agents_at_location) > 1:
                # Multiple agents in the same location - trigger interaction
                for i, agent in enumerate(agents_at_location):
                    other_agents = [a for j, a in enumerate(agents_at_location) if i != j]
                    
                    if other_agents:
                        # Determine interaction based on personalities, memories, and numbers
                        interaction_result = self._handle_location_interaction(agent, other_agents)
                        interactions.append(interaction_result)
        
        return interactions
    
    def _handle_location_interaction(self, agent, other_agents: List):
        """
        Handle interaction between agents at the same location based on personalities, 
        memories, and number of agents
        """
        agent_names = [a.name for a in other_agents]
        
        # Consider agent personality traits and past memories
        personality_factor = getattr(agent, 'personality_traits', [])
        memory_factor = agent.get_all_memories()  # Use agent's memories to influence behavior
        
        # If there are multiple agents, behavior might be different than one-on-one
        if len(other_agents) > 2:
            # Group setting - different dynamics
            topic = "group discussion"
        else:
            # One-on-one or small group
            topic = "conversation"
        
        # Initiate interaction based on personality and memory
        if hasattr(agent, 'talk_to_agents_at_location'):
            result = agent.talk_to_agents_at_location(topic)
            return result
        else:
            # Fallback to basic interaction
            return f"{agent.name} acknowledged the presence of {agent_names} at {agent.location}"
    
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