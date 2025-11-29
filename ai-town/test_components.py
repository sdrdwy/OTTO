"""
Test script to verify all components of the AI Town simulation
"""
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator


def test_components():
    print("Testing AI Town Components...\n")
    
    # Test memory system
    print("1. Testing Memory System:")
    memory = ConversationMemory()
    memory.add_memory("TestAgent", "This is a test memory")
    recent_memories = memory.get_recent_memories("TestAgent")
    print(f"   Added memory and retrieved: {recent_memories}")
    print(f"   Memory summary: {memory.get_memory_summary()}\n")
    
    # Test world simulator
    print("2. Testing World Simulator:")
    world = WorldSimulator()
    print(f"   World map:\n{world.get_map()}")
    print(f"   Random location: {world.get_random_location()}")
    print(f"   Random event: {world.trigger_random_event()}\n")
    
    # Test agents
    print("3. Testing Agents:")
    expert = ExpertAgent("TestExpert", memory, world)
    student = StudentAgent("TestStudent", memory, world)
    print(f"   Expert created: {expert.name}, expertise: {expert.current_expertise}")
    print(f"   Student created: {student.name}, goal: {student.current_goal}")
    
    # Test interaction
    print("\n4. Testing Interaction:")
    response = expert.get_response("Hello, how are you?")
    print(f"   Expert response: {response}")
    
    response = student.get_response("What can you tell me about learning?")
    print(f"   Student response: {response}")
    
    # Test memory addition
    print("\n5. Testing Memory Addition:")
    expert.remember("This is a test memory from expert")
    student.remember("This is a test memory from student")
    expert_memories = memory.get_recent_memories("TestExpert")
    student_memories = memory.get_recent_memories("TestStudent")
    print(f"   Expert memories: {expert_memories}")
    print(f"   Student memories: {student_memories}")
    
    print("\nAll components tested successfully!")


if __name__ == "__main__":
    test_components()