"""
AI Town Simulation
A multi-agent system with students, experts, and interactive environments
"""
import os
import sys
from datetime import datetime
from typing import List

# Add the ai_town directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "ai_town"))

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