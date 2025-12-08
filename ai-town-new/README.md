# AI Town Simulation

A multi-agent simulation system with students, teachers, and interactive environments. The system simulates a school environment where agents follow schedules, interact with each other, learn from experts, and take exams to measure knowledge gain.

## Features

- **Five Agents**: One teacher (expert) and four students with distinct personalities
- **Dynamic Scheduling**: Each agent generates daily schedules based on personality, memories, and map information
- **Interactive World**: Agents can move between locations, engage in conversations, and participate in activities
- **Memory System**: Long-term memory storage with importance weighting
- **Knowledge Base**: Expert agent has access to a knowledge base for teaching
- **Examination System**: Pre and post-simulation exams to measure learning
- **Configurable Settings**: All settings stored in JSON configuration files

## Architecture

### Directory Structure
```
ai-town-new/
├── agents/                 # Agent classes
│   ├── base_agent.py       # Base agent class with memory and core functionality
│   ├── expert_agent.py     # Expert agent with knowledge base access
│   └── student_agent.py    # Student agent with learning capabilities
├── world/                  # World simulation manager
│   └── world_manager.py    # Manages agents, locations, and simulation flow
├── configs/                # Configuration files
│   ├── agents/             # Individual agent configurations
│   ├── world/              # World settings
│   ├── schedule/           # Schedule logic
│   └── memory/             # Memory settings
├── knowledge_base/         # Knowledge base for expert agent
├── exams/                  # Exam questions and results
├── memory/                 # Agent memory files (generated at runtime)
├── logs/                   # Simulation logs and results (generated at runtime)
└── main.py                 # Main simulation entry point
```

### Agent Configuration

Each agent has its own JSON configuration file in `configs/agents/` with the following structure:

- **Personality**: Character setting, behavior patterns, speaking style, and goals
- **Schedule Habits**: Preferred locations, activity preferences, and social preferences
- **Expertise**: Whether the agent is an expert and has knowledge base access

### World Configuration

The world is configured through JSON files in `configs/world/`:

- **config.json**: Main simulation settings (days, time periods, etc.)
- **map.json**: Location definitions with names, descriptions, and functions
- **daily_schedule.json**: Schedule logic and special date rules

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have configured your Tongyi API key in your environment variables.

3. Run the simulation:
```bash
python main.py
```

## Key Components

### BaseAgent
- Core functionality shared by all agents
- Memory management with long-term storage
- Movement and location tracking
- Dialogue initiation and participation
- Battle simulation interface

### ExpertAgent
- Inherits from BaseAgent
- Access to knowledge base
- Teaching capabilities
- Curriculum generation based on knowledge content
- Question answering using knowledge base

### StudentAgent
- Inherits from BaseAgent
- Learning capabilities
- Exam taking functionality
- Question asking to experts

### WorldManager
- Manages all agents and locations
- Processes simulation time periods
- Handles agent movement and interactions
- Runs pre/post simulation exams
- Prints map status and simulation progress

## Simulation Flow

1. **Initialization**: Load all agent configurations and create agent instances
2. **Pre-Simulation Exams**: All agents take baseline exam
3. **Daily Simulation Loop**:
   - Each day is divided into time periods
   - Agents generate daily schedules based on personality and context
   - Agents move to scheduled locations
   - Agents at same locations may engage in dialogue
   - Activities and interactions are recorded in memories
4. **Post-Simulation Exams**: All agents take final exam
5. **Results**: Compare pre/post exam results to measure learning

## Memory System

Each agent has its own long-term memory stored in JSONL format in the `memory/` directory. Memories have:
- Importance weighting
- Metadata for categorization
- Timestamps for temporal context

## Customization

You can customize the simulation by modifying the JSON configuration files:

- Add new agents by creating new JSON files in `configs/agents/`
- Modify locations in `configs/world/map.json`
- Adjust schedule logic in `configs/schedule/daily_schedule.json`
- Add new knowledge to the expert's knowledge base in `knowledge_base/knowledge.jsonl`
- Create new exam questions in `exams/exam.json`

## Requirements

- Python 3.8+
- Langchain and related libraries
- Tongyi Qwen API access