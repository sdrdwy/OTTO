import asyncio
from world_manager import WorldManager, run_exams


async def main():
    print("Initializing Multi-Agent Simulation with LangGraph and LangChain")
    print("="*60)
    
    # Initialize the world
    world_manager = WorldManager()
    
    # Run pre-simulation exams to establish baseline
    run_exams(world_manager)
    
    # Run the simulation
    print("\nStarting simulation...")
    final_state = await world_manager.run_simulation()
    
    # Run post-simulation exams to measure improvement
    print("\nSimulation completed. Running final exams...")
    run_exams(world_manager)  # This would show the post-simulation results
    
    print("\nSimulation finished!")
    print(f"Final state: Day {final_state.day - 1} completed")


if __name__ == "__main__":
    asyncio.run(main())