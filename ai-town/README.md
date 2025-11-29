# AI Town Simulation

A multi-agent system with memory and world simulation capabilities.

## Overview

AI Town is a simulation environment where AI agents interact with each other in a text-based world. It features:
- 5 agents (1 expert, 4 students)
- Memory system for conversations and events
- World simulation with multiple locations
- Multi-turn conversations with context

## Architecture

### Agents
- **Expert Agent**: Provides domain expertise and teaches students
- **Student Agents**: Learn from the expert and engage in discussions

### Memory System
- Stores conversation history
- Maintains context across interactions
- Enables long-term memory retention

### World Simulator
- Text-based map with multiple locations
- Location-based events
- Agent movement between locations

## Files Structure

```
ai-town/
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── agents/
│   ├── base_agent.py       # Base agent class
│   ├── expert_agent.py     # Expert agent implementation
│   └── student_agent.py    # Student agent implementation
├── memory/
│   └── conversation_memory.py  # Memory management system
└── world/
    └── world_simulator.py  # World simulation environment
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_actual_api_key_here
```

3. Run the simulation:
```bash
python main.py
```

## Features

- **Multi-turn Conversations**: Agents maintain context across interactions
- **Memory System**: Long-term memory storage and retrieval
- **World Simulation**: Agents interact in different locations
- **Educational Interactions**: Expert teaches students on various topics
- **Event System**: Dynamic world events affect agent behavior

## Customization

You can customize:
- Agent personalities and expertise areas
- World locations and events
- Memory retention parameters
- Conversation topics and dynamics