"""
Example script demonstrating the full persona system and long-term memory capabilities
"""
import os
import sys
from datetime import datetime

# Add the ai-town directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-town'))

from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from agents.persona_manager import persona_manager


def demonstrate_persona_system():
    print("=== AI Town Persona System Demonstration ===\n")
    
    # Initialize memory and world
    memory = ConversationMemory()
    world = WorldSimulator()
    
    print("1. Loading and listing available personas:")
    expert_personas = persona_manager.list_personas("Expert")
    student_personas = persona_manager.list_personas("Student")
    
    print(f"   Expert Personas: {expert_personas}")
    print(f"   Student Personas: {student_personas}")
    
    print("\n2. Creating agents with specific personas:")
    
    # Create an expert with math persona
    math_expert = ExpertAgent("Prof. Mathews", memory, world, persona_id="math_expert")
    print(f"   Math Expert: {math_expert.name}")
    print(f"   - Personality: {', '.join(math_expert.personality_traits)}")
    print(f"   - Expertise: {', '.join(math_expert.expertise[:3])}...")
    
    # Create a student with curious persona
    curious_student = StudentAgent("Alice", memory, world, persona_id="curious_student")
    print(f"   Curious Student: {curious_student.name}")
    print(f"   - Personality: {', '.join(curious_student.personality_traits)}")
    print(f"   - Learning Goals: {', '.join(curious_student.learning_goals[:2])}...")
    
    print("\n3. Demonstrating memory capabilities:")
    
    # Simulate some interactions and memories
    interactions = [
        "Taught Alice about calculus fundamentals",
        "Discussed the applications of derivatives in physics",
        "Explained the concept of limits using mathematical examples",
        "Worked through several practice problems together",
        "Reviewed algebraic foundations needed for calculus"
    ]
    
    for i, interaction in enumerate(interactions):
        math_expert.remember(interaction, "teaching_session")
        curious_student.remember(f"Learned that {interaction.lower()}", "learning_session")
        print(f"   Memory {i+1}: Added '{interaction[:30]}...'")
    
    print(f"\n   {math_expert.get_memory_summary()}")
    print(f"   {curious_student.get_memory_summary()}")
    
    print("\n4. Searching memories:")
    math_results = math_expert.search_memories("calculus")
    print(f"   Math Expert memories about 'calculus': {len(math_results)}")
    for result in math_results:
        print(f"     - {result['content']}")
    
    student_results = curious_student.search_memories("learned")
    print(f"   Student memories containing 'learned': {len(student_results)}")
    
    print("\n5. Demonstrating persona-influenced responses:")
    
    # Different agents respond to the same prompt based on their personas
    prompt = "How would you approach learning a new complex subject?"
    
    print(f"   Math Expert response: {math_expert.get_response(prompt)}")
    print(f"   Curious Student response: {curious_student.get_response(prompt)}")
    
    print("\n6. Demonstrating memory persistence:")
    
    # Save memories to file
    success = math_expert.save_memories_to_file("config/math_expert_session.json")
    if success:
        print("   Math expert memories saved successfully")
    
    # Create a new agent and load memories
    new_math_expert = ExpertAgent("Prof. Newton", memory, world, persona_id="math_expert")
    load_success = new_math_expert.load_memories_from_file("config/math_expert_session.json")
    if load_success:
        print(f"   New math expert loaded memories: {new_math_expert.get_memory_summary()}")
    
    print("\n7. Creating and using a new persona dynamically:")
    
    # Create a new persona programmatically
    new_persona = {
        "name": "PhilosophyExpert",
        "role": "Expert",
        "personality_traits": ["thoughtful", "reflective", "inquisitive", "deep-thinking"],
        "expertise": ["Ethics", "Metaphysics", "Epistemology", "Logic", "Aesthetics"],
        "communication_style": "reflective",
        "behavioral_patterns": [
            "poses thought-provoking questions",
            "encourages deep reflection",
            "examines underlying assumptions",
            "connects ideas across domains"
        ],
        "default_responses": {
            "greeting": "Welcome to a journey of philosophical inquiry!",
            "teaching": "Let us examine this concept from multiple perspectives.",
            "problem_solving": "What assumptions are we making here?"
        }
    }
    
    # Add the new persona to the manager
    persona_manager.add_persona("philosophy_expert", new_persona)
    
    # Create an agent with the new persona
    philosophy_expert = ExpertAgent("Prof. Socrates", memory, world, persona_id="philosophy_expert")
    print(f"   New Philosophy Expert: {philosophy_expert.name}")
    print(f"   - Personality: {', '.join(philosophy_expert.personality_traits)}")
    print(f"   - Expertise: {', '.join(philosophy_expert.expertise)}")
    
    # Test the new persona's response
    response = philosophy_expert.get_response("What is the meaning of knowledge?")
    print(f"   Philosophy Expert response: {response}")
    
    print("\n8. Demonstrating long-term memory archival:")
    
    # Add many memories to trigger long-term storage
    for i in range(50):
        math_expert.remember(f"Teaching session #{i+10}: Advanced calculus concept", "teaching")
    
    print(f"   After adding 50 more memories: {math_expert.get_memory_summary()}")
    
    # Show that some memories moved to long-term storage
    all_memories = math_expert.get_all_memories()
    recent_memories = math_expert.memory.get_recent_memories(math_expert.name, limit=100)
    
    print(f"   Total memories: {len(all_memories)}")
    print(f"   Recent memories: {len(recent_memories)}")
    print(f"   Long-term memories: {len(all_memories) - len(recent_memories)}")
    
    print("\n=== Persona System Demonstration Complete ===")


if __name__ == "__main__":
    demonstrate_persona_system()