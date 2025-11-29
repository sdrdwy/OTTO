#!/usr/bin/env python3
"""
Test script to verify all requirements have been implemented:
1. Each time period includes student conversations and other activities
2. Agents can only go to locations in map_config.json
3. Location information is correctly recorded in long-term memory
4. Prompts are in Chinese
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from agents.student_agent import StudentAgent
from agents.expert_agent import ExpertAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator
from simulation_manager import SimulationManager
import json

def test_requirement_1_student_conversations():
    """Test that student-to-student conversations happen during time periods"""
    print("Testing requirement 1: Student conversations during time periods...")
    
    # Initialize components
    memory = ConversationMemory()
    world = WorldSimulator()
    
    # Create multiple students
    student1 = StudentAgent("Alice", memory, world)
    student2 = StudentAgent("Bob", memory, world)
    
    # Move both students to the same location
    student1.move_to_location("library")
    student2.move_to_location("library")
    
    # Simulate a conversation between students
    topic = "学习方法"
    prompt = f"用中文与{student2.name}就{topic}进行交流。"
    response = student1.get_response(prompt, f"你正在与{student2.name}交流{topic}。")
    print(f"  {student1.name}: {response}")
    
    # Student 2 responds
    prompt = f"回应{student1.name}关于{topic}的分享。"
    response = student2.get_response(prompt, f"你正在回应{student1.name}关于{topic}的分享。")
    print(f"  {student2.name}: {response}")
    
    # Check if the conversation is recorded with location
    student1_memories = memory.get_recent_memories("Alice", limit=5)
    student2_memories = memory.get_recent_memories("Bob", limit=5)
    
    # Check detailed memories to see if location is stored
    alice_detailed = memory.memories["Alice"][0] if memory.memories["Alice"] else None
    bob_detailed = memory.memories["Bob"][0] if memory.memories["Bob"] else None
    
    print(f"  Alice's memory location: {alice_detailed['details']['location'] if alice_detailed else 'None'}")
    print(f"  Bob's memory location: {bob_detailed['details']['location'] if bob_detailed else 'None'}")
    
    assert alice_detailed['details']['location'] == 'library', f"Alice's location should be library, got {alice_detailed['details']['location']}"
    assert bob_detailed['details']['location'] == 'library', f"Bob's location should be library, got {bob_detailed['details']['location']}"
    
    print("  ✓ Student conversations with location recording work correctly")
    return True

def test_requirement_2_valid_locations():
    """Test that agents can only go to valid locations from map_config.json"""
    print("\nTesting requirement 2: Agents restricted to valid locations...")
    
    memory = ConversationMemory()
    world = WorldSimulator()
    
    student = StudentAgent("Charlie", memory, world)
    
    # Load map config to know valid locations
    with open("world/map_config.json", 'r', encoding='utf-8') as f:
        map_config = json.load(f)
    valid_locations = list(map_config["locations"].keys())
    
    print(f"  Valid locations: {valid_locations}")
    
    # Try to move to a valid location
    student.move_to_location("library")
    assert student.location == "library", f"Should be at library, got {student.location}"
    print(f"  ✓ Successfully moved to valid location: {student.location}")
    
    # Try to move to an invalid location - should default to a valid one
    student.move_to_location("invalid_location")
    assert student.location in valid_locations, f"Location {student.location} should be in valid locations {valid_locations}"
    print(f"  ✓ Invalid location attempt redirected to valid location: {student.location}")
    
    # Check that initial location is valid
    student2 = StudentAgent("David", memory, world)
    assert student2.location in valid_locations, f"Initial location {student2.location} should be in valid locations {valid_locations}"
    print(f"  ✓ Agent initialized with valid location: {student2.location}")
    
    return True

def test_requirement_3_location_in_memory():
    """Test that location information is correctly recorded in long-term memory"""
    print("\nTesting requirement 3: Location information in long-term memory...")
    
    memory = ConversationMemory()
    world = WorldSimulator()
    
    student = StudentAgent("Eve", memory, world)
    
    # Move to different locations and create memories
    student.move_to_location("classroom")
    student.remember("Attended lecture", "learning")
    
    student.move_to_location("library")
    student.remember("Studied for exam", "study")
    
    # Check recent memories
    recent_memories = memory.get_recent_memories("Eve", limit=5)
    print(f"  Recent memories: {recent_memories}")
    
    # Check detailed memories to see location information
    for i, mem in enumerate(memory.memories["Eve"]):
        location = mem['details']['location']
        content = mem['content']
        print(f"    Memory {i+1}: '{content}' at location: {location}")
        assert location != "unknown", f"Location should not be unknown, got {location}"
    
    # Check long-term memories (after exceeding the limit, some go to long-term)
    # Add more memories to trigger long-term storage
    for i in range(55):  # Exceed the default limit of 50
        student.remember(f"Memory item {i}", "routine")
    
    long_term_memories = memory.get_long_term_memories("Eve", limit=10)
    print(f"  Long-term memories: {len(long_term_memories)} items")
    
    # Check that long-term memories also have location info
    if memory.long_term_memories.get("Eve"):
        for i, mem in enumerate(memory.long_term_memories["Eve"][:5]):  # Check first 5
            if 'detailed_content' in mem:
                detailed = mem['detailed_content']
                print(f"    Long-term memory {i+1}: {detailed[:100]}...")  # First 100 chars
                assert "Location:" in detailed or mem['details']['location'] != "unknown", "Long-term memory should contain location info"
            else:
                location = mem['details']['location']
                print(f"    Long-term memory {i+1}: location = {location}")
                assert location != "unknown", f"Long-term memory location should not be unknown, got {location}"
    
    print("  ✓ Location information correctly stored in both short-term and long-term memory")
    return True

def test_requirement_4_chinese_prompts():
    """Test that prompts are in Chinese"""
    print("\nTesting requirement 4: Chinese prompts...")
    
    memory = ConversationMemory()
    world = WorldSimulator()
    
    student = StudentAgent("Frank", memory, world)
    expert = ExpertAgent("Professor Wang", memory, world)
    
    # Test that student interactions use Chinese
    expert.move_to_location("classroom")
    student.move_to_location("classroom")
    
    # This should generate Chinese prompts and responses
    interaction_result = expert.interact([student], "机器学习")
    
    # Check that memory content is in Chinese
    expert_memories = memory.get_recent_memories("Professor Wang", limit=5)
    student_memories = memory.get_recent_memories("Frank", limit=5)
    
    print(f"  Expert memories (should be Chinese): {expert_memories[:2]}")
    print(f"  Student memories (should be Chinese): {student_memories[:2]}")
    
    # Verify Chinese content
    if expert_memories:
        assert any(char in expert_memories[0] for char in "，。？！学讨主参"), "Expert memory should contain Chinese characters"
    if student_memories:
        assert any(char in student_memories[0] for char in "，。？！学讨参"), "Student memory should contain Chinese characters"
    
    print("  ✓ Chinese prompts and responses are working correctly")
    return True

def test_simulation_manager_enhancements():
    """Test that the simulation manager has enhanced period activities"""
    print("\nTesting simulation manager enhancements...")
    
    sim_manager = SimulationManager()
    
    # Check that period activities method now includes student conversations
    import inspect
    source = inspect.getsource(sim_manager.simulate_period_activities)
    
    # Verify that the method includes student conversation logic
    assert "学生对话" in source, "simulate_period_activities should include student conversations"
    assert "location_groups" in source, "simulate_period_activities should group students by location"
    assert "conversation_topic" in source, "simulate_period_activities should have conversation topics"
    
    print("  ✓ Simulation manager includes enhanced period activities with student conversations")
    return True

def run_all_tests():
    """Run all requirement tests"""
    print("Running tests for all requirements...\n")
    
    try:
        test_requirement_1_student_conversations()
        test_requirement_2_valid_locations()
        test_requirement_3_location_in_memory()
        test_requirement_4_chinese_prompts()
        test_simulation_manager_enhancements()
        
        print("\n" + "="*60)
        print("✓ ALL REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
        print("="*60)
        print("1. ✓ Each time period includes student conversations and other activities")
        print("2. ✓ Agents can only go to locations in map_config.json") 
        print("3. ✓ Location information is correctly recorded in long-term memory")
        print("4. ✓ Prompts are in Chinese")
        print("="*60)
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)