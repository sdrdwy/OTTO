"""
AI Town Simulation
A multi-agent system with students, experts, and interactive environments
"""
import json
from datetime import datetime, timedelta
from world.world_manager import WorldManager
import os


def main():
    print("Initializing AI Town Simulation...")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize the world manager
    world_manager = WorldManager()
    
    # Run pre-simulation exams to establish baseline
    print("\nRunning pre-simulation exams...")
    pre_exam_results = world_manager.run_pre_simulation_exams()
    print("Pre-simulation exam results:")
    for result in pre_exam_results:
        print(f"  {result['student']}: Score {result['exam_score']}% ({result['grade']})")
    
    # Save pre-exam results
    with open("logs/pre_simulation_exam_results.json", "w", encoding="utf-8") as f:
        json.dump(pre_exam_results, f, ensure_ascii=False, indent=2)
    
    # Get simulation parameters
    config_path = "configs/world/config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    simulation_days = config.get("simulation_days", 10)
    time_periods = config.get("time_periods", [
        "morning_class_1", 
        "morning_class_2", 
        "afternoon_class_1", 
        "afternoon_class_2", 
        "evening"
    ])
    
    print(f"\nStarting simulation for {simulation_days} days...")
    
    # Main simulation loop
    for day in range(simulation_days):
        current_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        print(f"\n{'='*20} DAY {day + 1} ({current_date}) {'='*20}")
        
        # Print initial map status for the day
        world_manager.print_map_status()
        
        # Process each time period of the day
        for period in time_periods:
            print(f"--- {period.upper().replace('_', ' ')} ---")
            
            # Process the time period
            period_events = world_manager.process_time_period(period, current_date)
            
            # Print summary of events for this period
            for event in period_events:
                if event.get("type") != "dialogue":  # Don't print dialogue here as it's verbose
                    print(f"  {event['agent']} moved to {event['location']} for {event['activity']}")
        
        # End of day summary
        print(f"\nEnd of Day {day + 1} summary:")
        world_manager.print_map_status()
    
    # Run post-simulation exams to measure learning
    print("\nRunning post-simulation exams...")
    post_exam_results = world_manager.run_post_simulation_exams()
    print("Post-simulation exam results:")
    for result in post_exam_results:
        print(f"  {result['student']}: Score {result['exam_score']}% ({result['grade']})")
    
    # Save post-exam results
    with open("logs/post_simulation_exam_results.json", "w", encoding="utf-8") as f:
        json.dump(post_exam_results, f, ensure_ascii=False, indent=2)
    
    # Compare results
    print("\nComparison of pre and post simulation results:")
    for pre_result in pre_exam_results:
        post_result = next((r for r in post_exam_results if r["student"] == pre_result["student"]), None)
        if post_result:
            score_change = post_result["exam_score"] - pre_result["exam_score"]
            print(f"  {pre_result['student']}: {pre_result['exam_score']}% -> {post_result['exam_score']}% "
                  f"({'+' if score_change >= 0 else ''}{score_change}%)")
    
    # Save detailed logs
    all_agent_memories = {}
    for agent_id, agent in world_manager.agents.items():
        all_agent_memories[agent.name] = [mem.dict() for mem in agent.long_term_memory]
    
    with open("logs/final_agent_memories.json", "w", encoding="utf-8") as f:
        json.dump(all_agent_memories, f, ensure_ascii=False, indent=2)
    
    print(f"\nSimulation completed! Results saved to logs/ directory.")


if __name__ == "__main__":
    main()