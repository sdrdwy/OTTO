import json
import os
from typing import List, Dict, Any

from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.memory_manager import MemoryManager
from world.world_manager import WorldManager


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def main():
    # Load main configuration
    config = load_config("./config/config.json")
    
    # Initialize memory manager
    memory_manager = MemoryManager(
        memory_file_path=config["memory_file_path"],
        capacity=config["memory_capacity"]
    )
    
    # Initialize world manager
    world_manager = WorldManager(
        world_config_path=config["world_map_path"],
        schedule_config_path=config["schedule_path"]
    )
    
    # Create agents
    teacher = ExpertAgent(
        config_path="./config/agents/teacher.json",
        memory_manager=memory_manager,
        knowledge_base_path=config["knowledge_base_path"]
    )
    
    student1 = StudentAgent(
        config_path="./config/agents/student1.json",
        memory_manager=memory_manager
    )
    
    student2 = StudentAgent(
        config_path="./config/agents/student2.json",
        memory_manager=memory_manager
    )
    
    student3 = StudentAgent(
        config_path="./config/agents/student3.json",
        memory_manager=memory_manager
    )
    
    student4 = StudentAgent(
        config_path="./config/agents/student4.json",
        memory_manager=memory_manager
    )
    
    # Register agents with the world
    world_manager.register_agent(teacher.name, teacher)
    world_manager.register_agent(student1.name, student1)
    world_manager.register_agent(student2.name, student2)
    world_manager.register_agent(student3.name, student3)
    world_manager.register_agent(student4.name, student4)
    
    # Generate exam before simulation
    print("Generating exam...")
    exam_questions = world_manager.generate_exam(
        knowledge_base_path=config["knowledge_base_path"],
        num_questions=config["exam_questions_count"]
    )
    print(f"Generated {len(exam_questions)} exam questions")
    
    # Conduct pre-simulation exam
    print("\nConducting pre-simulation exam...")
    pre_exam_scores = world_manager.conduct_exam([teacher, student1, student2, student3, student4])
    print("Pre-simulation exam scores:")
    for agent_name, score in pre_exam_scores.items():
        print(f"  {agent_name}: {score}%")
    
    # Generate teaching outline for the teacher
    teacher.generate_teaching_outline(config["simulation_days"])
    print(f"\nGenerated teaching outline for {config['simulation_days']} days")
    
    # Run the simulation
    print(f"\nStarting simulation for {config['simulation_days']} days...")
    simulation_results = world_manager.run_simulation(
        days=config["simulation_days"],
        time_periods=config["time_periods"],
        max_dialogue_rounds=config["max_dialogue_rounds"]
    )
    
    # Conduct post-simulation exam
    print("\nConducting post-simulation exam...")
    post_exam_scores = world_manager.conduct_exam([teacher, student1, student2, student3, student4])
    print("Post-simulation exam scores:")
    for agent_name, score in post_exam_scores.items():
        print(f"  {agent_name}: {score}%")
    
    # Print score improvements
    print("\nScore improvements:")
    for agent_name in pre_exam_scores.keys():
        pre_score = pre_exam_scores[agent_name]
        post_score = post_exam_scores[agent_name]
        improvement = post_score - pre_score
        print(f"  {agent_name}: {pre_score}% -> {post_score}% ({improvement:+.2f}%)")
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    main()