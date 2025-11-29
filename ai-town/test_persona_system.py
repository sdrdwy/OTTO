"""
Demo script to test the persona system and enhanced memory functionality
"""
import os
import sys
import json
from datetime import datetime

# Add the ai-town directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-town'))

from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from agents.persona_manager import persona_manager


def test_persona_system():
    print("=== Testing Persona System ===\n")
    
    # Show available personas
    print("Available Expert Personas:")
    expert_personas = persona_manager.list_personas("Expert")
    for persona_id in expert_personas:
        print(f"  - {persona_id}")
    
    print("\nAvailable Student Personas:")
    student_personas = persona_manager.list_personas("Student")
    for persona_id in student_personas:
        print(f"  - {persona_id}")
    
    # Initialize memory and world
    memory = ConversationMemory()
    world = WorldSimulator()
    
    print("\n=== Creating Agents with Different Personas ===\n")
    
    # Create expert agents with different personas
    math_expert = ExpertAgent("MathExpert", memory, world, persona_id="math_expert")
    science_expert = ExpertAgent("ScienceExpert", memory, world, persona_id="science_expert")
    
    # Create student agents with different personas
    curious_student = StudentAgent("CuriousStudent", memory, world, persona_id="curious_student")
    analytical_student = StudentAgent("AnalyticalStudent", memory, world, persona_id="analytical_student")
    
    # Create agents without personas (default behavior)
    default_expert = ExpertAgent("DefaultExpert", memory, world)
    default_student = StudentAgent("DefaultStudent", memory, world)
    
    print("Math Expert Details:")
    print(f"  Name: {math_expert.name}")
    print(f"  Role: {math_expert.role}")
    print(f"  Personality Traits: {math_expert.personality_traits}")
    print(f"  Communication Style: {math_expert.communication_style}")
    print(f"  Behavioral Patterns: {math_expert.behavioral_patterns}")
    print(f"  Expertise: {math_expert.expertise}")
    
    print(f"\nScience Expert Details:")
    print(f"  Name: {science_expert.name}")
    print(f"  Role: {science_expert.role}")
    print(f"  Personality Traits: {science_expert.personality_traits}")
    print(f"  Communication Style: {science_expert.communication_style}")
    print(f"  Behavioral Patterns: {science_expert.behavioral_patterns}")
    print(f"  Expertise: {science_expert.expertise}")
    
    print(f"\nCurious Student Details:")
    print(f"  Name: {curious_student.name}")
    print(f"  Role: {curious_student.role}")
    print(f"  Personality Traits: {curious_student.personality_traits}")
    print(f"  Communication Style: {curious_student.communication_style}")
    print(f"  Behavioral Patterns: {curious_student.behavioral_patterns}")
    print(f"  Learning Goals: {curious_student.learning_goals}")
    
    print(f"\nAnalytical Student Details:")
    print(f"  Name: {analytical_student.name}")
    print(f"  Role: {analytical_student.role}")
    print(f"  Personality Traits: {analytical_student.personality_traits}")
    print(f"  Communication Style: {analytical_student.communication_style}")
    print(f"  Behavioral Patterns: {analytical_student.behavioral_patterns}")
    print(f"  Learning Goals: {analytical_student.learning_goals}")
    
    print(f"\nDefault Expert Details:")
    print(f"  Name: {default_expert.name}")
    print(f"  Role: {default_expert.role}")
    print(f"  Personality Traits: {default_expert.personality_traits}")
    print(f"  Communication Style: {default_expert.communication_style}")
    print(f"  Behavioral Patterns: {default_expert.behavioral_patterns}")
    
    print(f"\nDefault Student Details:")
    print(f"  Name: {default_student.name}")
    print(f"  Role: {default_student.role}")
    print(f"  Personality Traits: {default_student.personality_traits}")
    print(f"  Communication Style: {default_student.communication_style}")
    print(f"  Behavioral Patterns: {default_student.behavioral_patterns}")
    
    print("\n=== Testing Enhanced Memory Functionality ===\n")
    
    # Test memory operations
    print("Testing memory operations...")
    
    # Add some memories
    math_expert.remember("Discussed algebraic equations with students", "teaching")
    math_expert.remember("Explained calculus concepts", "teaching")
    math_expert.remember("Solved a complex math problem", "problem_solving")
    
    # Add more memories to test long-term storage
    for i in range(10):
        math_expert.remember(f"Memory {i}: Practiced mathematical proofs", "learning")
    
    # Get memory summary
    print(f"Math Expert Memory Summary: {math_expert.get_memory_summary()}")
    
    # Get all memories
    all_memories = math_expert.get_all_memories()
    print(f"Total memories retrieved: {len(all_memories)}")
    
    # Search memories
    search_results = math_expert.search_memories("math")
    print(f"Memories containing 'math': {len(search_results)}")
    for result in search_results:
        print(f"  - {result['content']}")
    
    # Save memories to file
    print("\nSaving memories to file...")
    math_expert.save_memories_to_file("test_memories.json")
    
    # Create a new agent and load memories
    print("\nTesting memory loading...")
    new_expert = ExpertAgent("NewMathExpert", memory, world, persona_id="math_expert")
    success = new_expert.load_memories_from_file("test_memories.json")
    if success:
        print(f"New expert memory summary after loading: {new_expert.get_memory_summary()}")
    
    print("\n=== Testing Agent Interactions ===\n")
    
    # Simple interaction test
    print("Math Expert response:")
    response = math_expert.get_response("Explain the concept of derivatives in calculus.")
    print(f"  {response}")
    
    print("\nCurious Student response:")
    response = curious_student.get_response("What is the most interesting thing about mathematics?")
    print(f"  {response}")
    
    print("\nAnalytical Student response:")
    response = analytical_student.get_response("How would you approach solving a complex mathematical problem?")
    print(f"  {response}")
    
    print("\n=== Persona System Test Complete ===")


if __name__ == "__main__":
    test_persona_system()