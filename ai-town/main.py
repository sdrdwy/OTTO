"""
AI Town Simulation
A multi-agent system with memory and world simulation
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator

# Load environment variables
load_dotenv()

def main():
    print("Initializing AI Town Simulation...")
    
    # Initialize components
    memory = ConversationMemory()
    world = WorldSimulator()
    
    # Create expert agent
    expert = ExpertAgent("Expert", memory, world)
    
    # Create student agents
    students = [
        StudentAgent(f"Student_{i}", memory, world) 
        for i in range(1, 5)
    ]
    
    # Start the simulation
    print("AI Town Simulation started!")
    print("World map:")
    print(world.get_map())
    
    # Schedule some events
    print("\n--- Scheduling Events ---")
    meeting_time = datetime.now() + timedelta(hours=1)
    meeting_end = meeting_time + timedelta(minutes=30)
    
    # Schedule a study group meeting
    meeting_id = expert.schedule_meeting(students[:2], "Study Group Session", meeting_time, meeting_end, 
                                       "Group study session for advanced topics", "Library")
    if meeting_id:
        print(f"Meeting scheduled with ID: {meeting_id}")
    
    # Schedule individual events
    event_time = datetime.now() + timedelta(hours=2)
    event_end = event_time + timedelta(hours=1)
    expert.schedule_event("Research Work", event_time, event_end, "Working on a research project", "Lab")
    
    print(f"\nExpert's calendar summary:")
    print(expert.get_calendar_summary())
    
    # Example interaction
    print("\nStarting conversation simulation...")
    expert.interact_with_students(students)
    
    # Additional activities
    print("\n--- Additional Activities ---")
    expert.facilitate_debate(students[:3], "the impact of AI on education")
    
    print(f"\nExpert's upcoming events:")
    upcoming = expert.get_upcoming_events(24)
    for event in upcoming:
        print(f"- {event['title']} at {event['start_time']}")

if __name__ == "__main__":
    main()