"""
Logging System for AI Town Simulation
Manages logging of simulation events, interactions, and state changes
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class SimulationLogger:
    def __init__(self, log_file: str = "simulation_log.json"):
        self.log_file = log_file
        self.logs = {
            "simulation_start": datetime.now().isoformat(),
            "events": [],
            "interactions": [],
            "agent_movements": [],
            "daily_summaries": [],
            "simulation_end": None
        }
    
    def log_event(self, event_type: str, description: str, agents_involved: List[str] = None, 
                  location: str = None, timestamp: str = None):
        """Log a general event"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "description": description,
            "agents_involved": agents_involved or [],
            "location": location
        }
        
        self.logs["events"].append(event)
    
    def log_interaction(self, agent1: str, agent2: str, interaction_type: str, 
                       topic: str, content: str, location: str = None, timestamp: str = None):
        """Log an interaction between agents"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        interaction = {
            "timestamp": timestamp,
            "type": interaction_type,
            "participants": [agent1, agent2],
            "topic": topic,
            "content": content,
            "location": location
        }
        
        self.logs["interactions"].append(interaction)
    
    def log_agent_movement(self, agent_name: str, from_location: str, to_location: str, 
                          timestamp: str = None):
        """Log agent movement between locations"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        movement = {
            "timestamp": timestamp,
            "agent": agent_name,
            "from": from_location,
            "to": to_location
        }
        
        self.logs["agent_movements"].append(movement)
    
    def log_daily_summary(self, day: int, summary: str, timestamp: str = None):
        """Log a daily summary"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        daily_summary = {
            "timestamp": timestamp,
            "day": day,
            "summary": summary
        }
        
        self.logs["daily_summaries"].append(daily_summary)
    
    def save_log(self, filename: str = None):
        """Save logs to file"""
        if filename is None:
            filename = self.log_file
        
        self.logs["simulation_end"] = datetime.now().isoformat()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=2, default=str)
            print(f"Simulation log saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving log: {e}")
            return False
    
    def get_logs(self) -> Dict[str, Any]:
        """Get all logs"""
        return self.logs
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = {
            "simulation_start": datetime.now().isoformat(),
            "events": [],
            "interactions": [],
            "agent_movements": [],
            "daily_summaries": [],
            "simulation_end": None
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """Get simulation statistics"""
        return {
            "total_events": len(self.logs["events"]),
            "total_interactions": len(self.logs["interactions"]),
            "total_movements": len(self.logs["agent_movements"]),
            "total_daily_summaries": len(self.logs["daily_summaries"])
        }