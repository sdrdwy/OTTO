# Multi-Agent Simulation System

This project implements a multi-agent simulation system with the following features:

## Overview

The system simulates a world with 5 agents (1 teacher and 4 students) that interact with each other, move around a map, engage in dialogues, and participate in learning activities. The simulation includes memory management, knowledge bases, and scheduled activities.

## Architecture

### Agents
- **Teacher Agent**: An expert agent with access to a knowledge base, responsible for teaching students
- **Student Agents**: Four students with different personalities and learning behaviors

### Configuration
Each agent has its own JSON configuration file in `config/agents/` containing:
- Name and role
- Personality traits
- Dialogue style
- Schedule preferences
- Daily habits

### World Management
- Map with multiple locations (classroom, library, cafeteria, playground, office)
- Scheduled activities based on time periods
- Agent movement and location tracking

### Memory System
- Short-term and long-term memory storage
- Memory retrieval based on relevance and access frequency
- Memory modification and weight adjustment

### Knowledge Base
- Stored in JSONL format
- Accessible by the expert agent (teacher)
- Used for generating teaching content and answering questions

## Features

1. **Daily Scheduling**: Agents create daily schedules based on personal preferences and mandatory activities
2. **Movement System**: Agents can move between different locations in the world
3. **Dialogue System**: Multi-round conversations between agents
4. **Teaching System**: Teacher provides lessons based on a generated curriculum
5. **Memory System**: Agents maintain both short-term and long-term memories
6. **Examination System**: Pre- and post-simulation exams to measure learning
7. **Battle System**: Simple simulation of agent interactions (placeholder functionality)

## Configuration Files

- `config/config.json`: Main system configuration
- `config/world.json`: World map and initial positions
- `config/schedule.json`: Daily schedule and mandatory activities
- `config/agents/*.json`: Individual agent configurations
- `knowledge_base/knowledge.jsonl`: Knowledge base for the teacher
- `memory/memory.jsonl`: Memory storage (created during runtime)

## Time Periods

The day is divided into 5 time periods:
- Morning
- Mid-morning
- Afternoon
- Late afternoon
- Evening

## Running the Simulation

```bash
python simulator.py
```

The simulation will:
1. Generate an exam based on the knowledge base
2. Conduct a pre-simulation exam
3. Run the daily simulation for the configured number of days
4. Conduct a post-simulation exam
5. Report score improvements

## Customization

You can customize the simulation by modifying:
- Agent personalities and preferences in `config/agents/`
- World locations in `config/world.json`
- Daily schedules in `config/schedule.json`
- Knowledge content in `knowledge_base/knowledge.jsonl`
- System parameters in `config/config.json`