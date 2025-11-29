"""
AI Town Simulation
A multi-agent system with memory and world simulation
"""
import os
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
    
    # Example interaction
    print("\nStarting conversation simulation...")
    expert.interact_with_students(students)

if __name__ == "__main__":
    main()