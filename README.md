# AI Town Simulation

A multi-agent simulation system that models an educational environment with teachers, students, and interactive world dynamics.

## 🏗️ Project Structure

```
/workspace/
├── agents/                    # Agent classes and logic
│   ├── agent_base.py          # Base agent class
│   ├── expert_agent.py        # Expert agent (teacher) class
│   └── student_agent.py       # Student agent class
├── world/                     # World management system
│   ├── world_manager.py       # World state and location management
│   └── exam_system.py         # Examination and assessment system
├── memory/                    # Memory management system
│   └── memory_manager.py      # Long-term and short-term memory
├── knowledge_base/            # Knowledge base for expert agent
│   └── knowledge.jsonl        # JSONL format knowledge entries
├── config/                    # Configuration files
│   ├── config.json            # Main configuration
│   ├── world.json             # World/map configuration
│   ├── schedule.json          # Daily schedule configuration
│   └── agents/                # Individual agent configurations
│       ├── teacher.json
│       ├── student1.json
│       ├── student2.json
│       ├── student3.json
│       └── student4.json
├── simulator.py               # Main simulation controller
└── requirements.txt           # Python dependencies
```

## 🎯 Core Features

### 1. Agent System
- **Teacher Agent**: Expert agent with access to knowledge base
- **Student Agents**: Four unique students with different personalities
- Each agent has individual JSON configuration for persona, schedule habits, etc.

### 2. World Management
- **Map System**: Classroom, library, playground, cafeteria, dormitory
- **Location Management**: Agents move between locations based on activities
- **Schedule System**: Daily schedule with five time periods

### 3. Memory System
- **Long-term Memory**: JSONL-based storage with access weighting
- **Memory Retrieval**: Searchable by agent, type, content, and related agents
- **Memory Evolution**: Memories can be updated and weighted based on access

### 4. Knowledge Base
- **JSONL Format**: Segmented knowledge storage
- **Category-based**: Organized by subject matter
- **Curriculum Generation**: Automatic curriculum from knowledge base

### 5. Examination System
- **Pre/Post Testing**: Assessment before and after simulation
- **Performance Tracking**: Score improvement analysis
- **Adaptive Questions**: Based on knowledge base content

## ⚙️ Configuration

### Main Configuration (`config/config.json`)
- `max_round`: Maximum rounds for multi-agent conversations
- `simulation_days`: Number of days to simulate
- `time_periods`: Daily time divisions
- `exam_questions_count`: Number of questions in exams
- `memory_capacity`: Maximum memories to retain

### Agent Configurations
Each agent has a JSON file with:
- `persona`: Character description and behavior patterns
- `is_expert`: Whether agent has access to knowledge base
- `dialogue_style`: Communication approach
- `schedule_habits`: Preferred activities for each time period
- `作息习惯`: Daily routine preferences

### World Configuration (`config/world.json`)
- Map locations with descriptions and purposes
- Initial agent positions

### Schedule Configuration (`config/schedule.json`)
- Daily schedule template
- Special date schedules
- Required activities for agents

## 🚀 Running the Simulation

```bash
python simulator.py
```

The simulation will:
1. Conduct pre-simulation examinations
2. Run daily activities across multiple time periods
3. Execute agent interactions, learning, and memory formation
4. Conduct post-simulation examinations
5. Display performance comparison

## 🎓 Educational Simulation Flow

1. **Initialization**: Load agents, world, and knowledge base
2. **Pre-Testing**: Assess baseline knowledge
3. **Daily Simulation**:
   - Morning classes (teacher instruction, student learning)
   - Study sessions
   - Free time activities
   - Group activities
   - Evening rest
4. **Memory Formation**: Agents create memories from interactions
5. **Post-Testing**: Assess knowledge improvement
6. **Analysis**: Compare pre/post performance

## 🧠 Agent Behaviors

### Teacher (Expert Agent)
- Generates curriculum from knowledge base
- Conducts lessons and answers questions
- Assesses student understanding
- Maintains and updates knowledge base

### Students
- Follow individual learning patterns
- Participate in classes and group activities
- Ask questions and seek help
- Develop learning progress over time
- Collaborate with classmates

## 📊 Memory System Features

- **Weighted Access**: Frequently accessed memories have higher priority
- **Relevance Search**: Find memories based on content, type, and context
- **Capacity Management**: Maintain memory quality by limiting quantity
- **Cross-Agent Memories**: Track interactions between multiple agents

## 📚 Knowledge Base Structure

The knowledge base uses JSONL format with flexible fields:
```json
{"id": 1, "category": "math", "content": "Mathematical concept description"}
{"id": 2, "category": "science", "content": "Scientific principle explanation"}
```

This allows for diverse knowledge types and easy expansion.