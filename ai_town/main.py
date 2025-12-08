#!/usr/bin/env python3
"""
AI Town Simulation
A multi-agent simulation environment with teachers, students, and interactive world dynamics.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add workspace to Python path
sys.path.append('/workspace')

from world.simulation_engine import SimulationEngine


def main():
    """
    Main function to run the AI Town simulation
    """
    print("Welcome to AI Town Simulation!")
    print("Initializing simulation environment...")
    
    try:
        # Create and run the simulation
        simulation = SimulationEngine()
        simulation.run_simulation()
        
    except Exception as e:
        print(f"An error occurred during simulation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nSimulation completed!")


if __name__ == "__main__":
    main()