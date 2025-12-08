#!/usr/bin/env python3
"""
AI Town Simulation
A multi-agent system with students, experts, and interactive environments
"""
from simulation_manager import SimulationManager


def main():
    print("Initializing AI Town Simulation...")
    
    # Initialize the simulation manager
    sim_manager = SimulationManager()
    
    # Run the complete simulation
    sim_manager.run_simulation()
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    main()