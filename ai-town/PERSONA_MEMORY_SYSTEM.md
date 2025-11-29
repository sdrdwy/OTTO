# AI Town Persona and Memory System

This document explains how to use the persona and enhanced memory system in AI Town.

## Overview

The AI Town system now supports:
- Different agent personalities stored in JSON files
- Enhanced long-term memory management
- Memory search and persistence capabilities
- Dynamic persona loading and creation

## Persona System

### Creating Personas

Personas are defined in JSON files located in the `personas/` directory. Each persona file contains multiple persona definitions:

```json
{
  "persona_id": {
    "name": "Display Name",
    "role": "Expert|Student",
    "personality_traits": ["trait1", "trait2", ...],
    "expertise": ["topic1", "topic2", ...],
    "communication_style": "style",
    "behavioral_patterns": ["pattern1", "pattern2", ...],
    "default_responses": {
      "greeting": "Greeting message",
      "teaching": "Teaching response",
      "problem_solving": "Problem solving approach"
    }
  }
}
```

### Using Personas

To create an agent with a specific persona:

```python
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator

memory = ConversationMemory()
world = WorldSimulator()

# Create an expert with a math persona
math_expert = ExpertAgent("Math Teacher", memory, world, persona_id="math_expert")

# Create a student with a curious persona
curious_student = StudentAgent("Student Alice", memory, world, persona_id="curious_student")
```

### Available Personas

- **Expert Personas:**
  - `math_expert`: Analytical, logical, precise expert in mathematics
  - `science_expert`: Curious, evidence-based expert in science
  - `literature_expert`: Expressive, thoughtful expert in literature

- **Student Personas:**
  - `curious_student`: Inquisitive student who asks many questions
  - `analytical_student`: Methodical student who analyzes systematically
  - `creative_student`: Creative student who thinks outside the box

## Enhanced Memory System

### Memory Types

- **Short-term memories**: Recent events (limited by `max_memories_per_agent`)
- **Long-term memories**: Archived memories stored permanently

### Memory Operations

```python
# Add a memory
agent.remember("Event description", memory_type="conversation")

# Add explicitly to long-term memory
agent.remember_long_term("Important information", memory_type="important")

# Search memories
results = agent.search_memories("query")

# Get all memories
all_memories = agent.get_all_memories()

# Get memory summary
summary = agent.get_memory_summary()

# Save memories to file
agent.save_memories_to_file("my_memories.json")

# Load memories from file
agent.load_memories_from_file("my_memories.json")
```

### Memory Persistence

Memories are automatically managed:
- When short-term memory limit is reached, oldest memories move to long-term storage
- Long-term memories are saved to `long_term_memory.json`
- Custom memory files can be saved/loaded as needed

## Dynamic Persona Management

### Adding New Personas at Runtime

```python
from agents.persona_manager import persona_manager

new_persona = {
    "name": "NewExpert",
    "role": "Expert",
    "personality_traits": ["innovative", "creative"],
    "expertise": ["Innovation", "Creativity"],
    # ... other fields
}

# Add to persona manager
persona_manager.add_persona("innovative_expert", new_persona)

# Create agent with new persona
new_agent = ExpertAgent("Innovation Expert", memory, world, persona_id="innovative_expert")
```

### Listing Available Personas

```python
# List all personas
all_personas = persona_manager.list_personas()

# List personas by role
expert_personas = persona_manager.list_personas("Expert")
student_personas = persona_manager.list_personas("Student")
```

## Example Usage

```python
from agents.expert_agent import ExpertAgent
from agents.student_agent import StudentAgent
from memory.conversation_memory import ConversationMemory
from world.world_simulator import WorldSimulator

# Initialize
memory = ConversationMemory()
world = WorldSimulator()

# Create agents with personas
math_expert = ExpertAgent("Prof. Math", memory, world, persona_id="math_expert")
curious_student = StudentAgent("Alice", memory, world, persona_id="curious_student")

# Interact and create memories
math_expert.remember("Taught calculus to Alice", "teaching")
curious_student.remember("Learned calculus from Prof. Math", "learning")

# Search memories
teaching_memories = math_expert.search_memories("calculus")
learning_memories = curious_student.search_memories("calculus")

# Save and load memories
math_expert.save_memories_to_file("session_1.json")
new_expert = ExpertAgent("New Prof", memory, world, persona_id="math_expert")
new_expert.load_memories_from_file("session_1.json")
```

## File Structure

```
ai-town/
├── personas/
│   ├── expert_personas.json
│   └── student_personas.json
├── agents/
│   ├── base_agent.py      # Enhanced with persona support
│   ├── expert_agent.py    # Updated constructor
│   ├── student_agent.py   # Updated constructor
│   └── persona_manager.py # New persona management system
├── memory/
│   └── conversation_memory.py  # Enhanced with search and persistence
└── examples/
    ├── test_persona_system.py
    └── example_persona_usage.py
```

The persona and memory system provides a flexible framework for creating diverse AI agents with persistent, searchable memory capabilities.