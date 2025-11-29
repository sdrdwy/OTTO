#!/usr/bin/env python3
"""
Test script to verify the location fix and Chinese prompts
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ai_town"))

from agents.student_agent import StudentAgent
from agents.expert_agent import ExpertAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator

def test_location_storage():
    print("Testing location storage fix...")
    
    # Initialize components
    memory = ConversationMemory()
    world = WorldSimulator()
    
    # Create agents
    student = StudentAgent("Alice", memory, world)
    expert = ExpertAgent("Professor Smith", memory, world)
    
    # Move agents to specific locations
    student.move_to_location("library")
    expert.move_to_location("classroom")
    
    print(f"Student location: {student.location}")
    print(f"Expert location: {expert.location}")
    
    # Test that remember method properly stores location
    student.remember("Test memory", "test")
    expert.remember("Test memory", "test")
    
    # Check recent memories to see if location is stored
    student_memories = memory.get_recent_memories("Alice", limit=5)
    expert_memories = memory.get_recent_memories("Professor Smith", limit=5)
    
    print(f"Alice's recent memories: {student_memories}")
    print(f"Professor Smith's recent memories: {expert_memories}")
    
    # Check detailed memories to see location information
    if "Alice" in memory.memories:
        alice_detailed = memory.memories["Alice"][0] if memory.memories["Alice"] else None
        if alice_detailed:
            print(f"Alice's detailed memory: {alice_detailed}")
            print(f"Alice's memory location: {alice_detailed['details']['location']}")
    
    if "Professor Smith" in memory.memories:
        expert_detailed = memory.memories["Professor Smith"][0] if memory.memories["Professor Smith"] else None
        if expert_detailed:
            print(f"Expert's detailed memory: {expert_detailed}")
            print(f"Expert's memory location: {expert_detailed['details']['location']}")
    
    # Test interaction with Chinese prompts
    print("\nTesting Chinese prompts...")
    expert.interact([student], "人工智能")
    
    # Check if location is properly stored in the interaction
    student_memories_after = memory.get_recent_memories("Alice", limit=5)
    expert_memories_after = memory.get_recent_memories("Professor Smith", limit=5)
    
    print(f"Alice's memories after interaction: {student_memories_after}")
    print(f"Expert's memories after interaction: {expert_memories_after}")
    
    # Check detailed memories after interaction
    if "Alice" in memory.memories and len(memory.memories["Alice"]) > 1:
        alice_detailed_after = memory.memories["Alice"][0]  # Most recent
        print(f"Alice's detailed memory after interaction: {alice_detailed_after}")
        print(f"Alice's memory location after interaction: {alice_detailed_after['details']['location']}")
    
    if "Professor Smith" in memory.memories and len(memory.memories["Professor Smith"]) > 1:
        expert_detailed_after = memory.memories["Professor Smith"][0]  # Most recent
        print(f"Expert's detailed memory after interaction: {expert_detailed_after}")
        print(f"Expert's memory location after interaction: {expert_detailed_after['details']['location']}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_location_storage()