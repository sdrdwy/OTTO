"""
Calendar/Schedule functionality for AI Town
Manages events, appointments, and schedules for agents
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os


class Calendar:
    def __init__(self, calendar_file: str = "calendar.json"):
        self.calendar_file = calendar_file
        self.events: Dict[str, List[Dict]] = self.load_calendar()
        
    def load_calendar(self) -> Dict[str, List[Dict]]:
        """Load calendar from file if it exists"""
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_calendar(self):
        """Save calendar to file"""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving calendar: {e}")
    
    def schedule_event(self, agent_name: str, title: str, start_time: datetime, end_time: datetime, description: str = "", location: str = "") -> str:
        """Schedule a new event for an agent"""
        if agent_name not in self.events:
            self.events[agent_name] = []
        
        event_id = f"event_{len(self.events[agent_name])}_{int(start_time.timestamp())}"
        
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "description": description,
            "location": location,
            "created_at": datetime.now().isoformat()
        }
        
        self.events[agent_name].append(event)
        self.save_calendar()
        
        return event_id
    
    def get_upcoming_events(self, agent_name: str, hours: int = 24) -> List[Dict]:
        """Get upcoming events for an agent within the specified hours"""
        if agent_name not in self.events:
            return []
        
        now = datetime.now()
        future_time = now + timedelta(hours=hours)
        
        upcoming = []
        for event in self.events[agent_name]:
            event_start = datetime.fromisoformat(event["start_time"])
            if now <= event_start <= future_time:
                upcoming.append(event)
        
        # Sort by start time
        upcoming.sort(key=lambda x: datetime.fromisoformat(x["start_time"]))
        return upcoming
    
    def get_events_on_date(self, agent_name: str, date: datetime) -> List[Dict]:
        """Get events for an agent on a specific date"""
        if agent_name not in self.events:
            return []
        
        date_str = date.date().isoformat()
        same_date_events = []
        
        for event in self.events[agent_name]:
            event_date = datetime.fromisoformat(event["start_time"]).date().isoformat()
            if event_date == date_str:
                same_date_events.append(event)
        
        # Sort by start time
        same_date_events.sort(key=lambda x: datetime.fromisoformat(x["start_time"]))
        return same_date_events
    
    def cancel_event(self, agent_name: str, event_id: str) -> bool:
        """Cancel an event by ID"""
        if agent_name not in self.events:
            return False
        
        for i, event in enumerate(self.events[agent_name]):
            if event["id"] == event_id:
                del self.events[agent_name][i]
                self.save_calendar()
                return True
        
        return False
    
    def reschedule_event(self, agent_name: str, event_id: str, new_start_time: datetime, new_end_time: datetime) -> bool:
        """Reschedule an existing event"""
        if agent_name not in self.events:
            return False
        
        for event in self.events[agent_name]:
            if event["id"] == event_id:
                event["start_time"] = new_start_time.isoformat()
                event["end_time"] = new_end_time.isoformat()
                event["updated_at"] = datetime.now().isoformat()
                self.save_calendar()
                return True
        
        return False
    
    def get_conflicting_events(self, agent_name: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Check for conflicting events in the given time range"""
        if agent_name not in self.events:
            return []
        
        conflicts = []
        for event in self.events[agent_name]:
            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])
            
            # Check if time ranges overlap
            if (start_time < event_end and end_time > event_start):
                conflicts.append(event)
        
        return conflicts
    
    def get_calendar_summary(self, agent_name: str) -> str:
        """Get a summary of the agent's calendar"""
        if agent_name not in self.events or not self.events[agent_name]:
            return f"{agent_name} has no scheduled events."
        
        summary = f"Calendar Summary for {agent_name}:\n"
        events = self.events[agent_name]
        
        # Group events by date
        events_by_date = {}
        for event in events:
            date = datetime.fromisoformat(event["start_time"]).date().isoformat()
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
        
        # Sort dates
        sorted_dates = sorted(events_by_date.keys())
        
        for date in sorted_dates:
            summary += f"\n{date}:\n"
            day_events = sorted(events_by_date[date], key=lambda x: datetime.fromisoformat(x["start_time"]))
            for event in day_events:
                start_time = datetime.fromisoformat(event["start_time"]).strftime("%H:%M")
                end_time = datetime.fromisoformat(event["end_time"]).strftime("%H:%M")
                summary += f"  {start_time}-{end_time}: {event['title']}"
                if event['location']:
                    summary += f" at {event['location']}"
                summary += "\n"
        
        return summary
    
    def schedule_meeting(self, participants: List[str], title: str, start_time: datetime, end_time: datetime, description: str = "", location: str = "") -> Optional[str]:
        """Schedule a meeting with multiple participants"""
        # Check for conflicts across all participants
        for participant in participants:
            conflicts = self.get_conflicting_events(participant, start_time, end_time)
            if conflicts:
                print(f"Conflict for {participant}: {conflicts[0]['title']} at {conflicts[0]['start_time']}")
                return None  # Cannot schedule due to conflict
        
        # Schedule the meeting for all participants
        event_id = None
        for participant in participants:
            if event_id is None:
                # Create the event for the first participant and get the ID
                event_id = self.schedule_event(participant, title, start_time, end_time, description, location)
            else:
                # Use the same event ID for other participants
                if participant not in self.events:
                    self.events[participant] = []
                
                event = {
                    "id": event_id,
                    "title": title,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "description": description,
                    "location": location,
                    "created_at": datetime.now().isoformat(),
                    "meeting_participants": participants
                }
                
                self.events[participant].append(event)
        
        self.save_calendar()
        return event_id