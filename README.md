# AI Town Simulation

A multi-agent simulation environment featuring teachers, students, and interactive world dynamics with memory and knowledge management.

## Overview

AI Town is a simulation environment where AI agents interact in a structured world with:

- **5 Agents**: 1 teacher (expert) and 4 students with distinct personalities
- **World Simulation**: Locations with specific functions and agent movement
- **Memory System**: Short-term and long-term memory with weighted recall
- **Knowledge Base**: Topic-based knowledge system for expert agents
- **Schedule System**: Daily schedules based on global requirements and personal preferences
- **Dialogue System**: Multi-agent conversations with topic-based participation
- **Assessment System**: Initial and final exams to measure learning progress

## Architecture

### Agents
- **Teacher Agent**: Expert with knowledge base access, curriculum generation, and teaching capabilities
- **Student Agents**: Each with unique personalities, learning behaviors, and memory systems

### World Components
- **World Manager**: Handles agent positions and location management
- **Simulation Engine**: Runs the day-by-day simulation
- **Map System**: Defines locations and their functions

### Memory System
- **Short-term Memory**: Recent events and interactions
- **Long-term Memory**: Weighted memories with access tracking
- **Memory Manager**: Handles storage and retrieval of agent memories

### Configuration
- **Agent Configs**: Individual JSON files for each agent's personality and behavior
- **World Configs**: Map, schedule, and global settings in JSON format
- **Simulation Configs**: Runtime parameters and settings

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API key:
```bash
# Copy the example and add your DashScope API key
cp .env.example .env
```

3. Run the simulation:
```bash
cd /workspace/ai_town
python main.py
```

## Features

- **Daily Scheduling**: Agents create personalized schedules based on global requirements and personal preferences
- **Location-Based Activities**: Different activities available in different locations
- **Multi-Agent Dialogues**: Conversations with topic-based participation decisions
- **Teaching/Learning**: Knowledge transfer from teacher to students
- **Memory Formation**: Automatic creation of short-term and long-term memories
- **Assessment**: Pre- and post-simulation evaluation to measure learning
- **Weighted Memory System**: Memories with adjustable weights based on importance and access frequency

## Configuration Files

- `configs/config.json`: Global simulation settings
- `configs/map.json`: World locations and descriptions
- `configs/schedule.json`: Global schedule constraints
- `configs/teacher.json`: Teacher agent configuration
- `configs/student1-4.json`: Individual student agent configurations
- `knowledge_base/*.jsonl`: Knowledge segments for expert agents
- `memory/*.jsonl`: Agent memory files (generated during simulation)

## File Structure

```
ai_town/
├── agents/                 # Agent classes and implementations
│   ├── __init__.py
│   ├── agent.py           # Base agent class
│   ├── teacher_agent.py   # Expert teacher agent
│   └── student_agent.py   # Student agent implementation
├── configs/               # Configuration files
│   ├── __init__.py
│   ├── config_loader.py   # Configuration loading utilities
│   └── *.json             # Various configuration files
├── exams/                 # Exam questions and results (generated)
├── knowledge_base/        # Knowledge segments for expert agents
│   ├── __init__.py
│   └── *.jsonl            # Knowledge base files
├── logs/                  # Simulation logs (generated)
├── memory/                # Agent memory files (generated)
│   ├── __init__.py
│   └── memory_manager.py  # Memory management utilities
├── world/                 # World simulation components
│   ├── __init__.py
│   ├── world_manager.py   # World state management
│   └── simulation_engine.py # Main simulation logic
├── main.py               # Entry point for the simulation
└── requirements.txt      # Python dependencies
```

## Customization

To customize the simulation:

1. Modify agent configurations in `configs/` to change personalities and behaviors
2. Update `map.json` to add or modify locations
3. Adjust `schedule.json` to change global scheduling constraints
4. Add knowledge to the knowledge base in `knowledge_base/` for the teacher agent
5. Modify the time periods in `config.json` to change the daily structure

## Requirements

- Python 3.8+
- DashScope API key for Qwen model access
- Dependencies listed in `requirements.txt`

## License

This project is licensed under the MIT License.