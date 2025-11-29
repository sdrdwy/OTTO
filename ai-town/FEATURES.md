# AI Town Features

## Overview
AI Town is a multi-agent simulation system with advanced features including Qwen model integration, long-term memory, diverse interactions, and calendar functionality.

## Key Features

### 1. Qwen Model Integration
- Replaced default OpenAI models with Alibaba Cloud's Qwen model
- Supports multiple LLM backends (Qwen, OpenAI, or mock for testing)
- Automatic fallback system if API keys are not provided
- Easy configuration via environment variables

### 2. Long-term Memory System
- Dual memory architecture (short-term and long-term)
- Automatic archival of old memories to long-term storage
- JSON-based persistence for long-term memories
- Memory search capabilities across both short and long-term storage
- Memory type categorization (conversation, teaching, learning, etc.)

### 3. Enhanced Interaction Models
- Multi-agent group discussions instead of one-on-one conversations
- Support for debates and structured discussions
- Group activity organization capabilities
- Diverse interaction methods (opinion sharing, question asking, etc.)
- Improved context awareness in conversations

### 4. Calendar and Scheduling System
- Individual agent calendars with event scheduling
- Meeting scheduling between multiple agents
- Conflict detection for scheduling
- Upcoming events tracking
- Calendar summary generation
- JSON-based calendar persistence

### 5. World Simulation Enhancements
- Location-based interactions
- Event scheduling within the world
- Agent presence tracking across locations
- World event management

## Usage

### Environment Setup
```bash
DASHSCOPE_API_KEY=your_qwen_api_key_here  # For Qwen model
OPENAI_API_KEY=your_openai_api_key_here    # For OpenAI fallback
```

### Running the Simulation
```bash
cd ai-town
python main.py
```

### Key Classes

#### BaseAgent
- Enhanced with calendar functionality
- Memory type support
- Multi-agent interaction methods

#### ExpertAgent
- Group discussion facilitation
- Debate organization
- Activity planning

#### StudentAgent
- Group interaction capabilities
- Opinion sharing
- Question asking in group settings

#### ConversationMemory
- Dual memory storage (short/long-term)
- Automatic archival system
- Search functionality

#### Calendar
- Event scheduling
- Conflict detection
- Meeting coordination

#### WorldSimulator
- Integrated calendar system
- Location management
- Event coordination

## Configuration

The system supports multiple LLM backends with the following priority:
1. Qwen (requires DASHSCOPE_API_KEY)
2. OpenAI (requires OPENAI_API_KEY)
3. Mock (for testing without API keys)

Memory limits can be configured in the ConversationMemory class.
Calendar data is persisted in `calendar.json`.
Long-term memory is persisted in `long_term_memory.json`.