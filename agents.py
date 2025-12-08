import json
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from memory_manager import MemoryManager
from knowledge_base import KnowledgeBase
import config


class AgentState(BaseModel):
    """State for the agent"""
    agent_id: str
    day: int
    time_period: str
    location: str
    personality: str
    schedule: List[str]
    memory: List[str]
    dialogue_memory: List[Dict[str, Any]]
    long_term_memory: List[Dict[str, Any]]
    knowledge_access: bool
    dialogue_requests: List[Dict[str, Any]]
    current_dialogue: Optional[Dict[str, Any]] = None
    battle_result: Optional[Dict[str, Any]] = None
    current_action: str = ""
    action_result: Optional[str] = None
    position: str = ""


class ScheduleTool(BaseTool):
    name = "schedule_tool"
    description = "Tool for agent to plan their daily schedule"

    def _run(self, agent_state: AgentState) -> str:
        # Based on total schedule logic, personal persona, map information, and saved personal memories
        schedule_parts = []
        total_schedule = config.TOTAL_SCHEDULE
        
        # Generate a personalized schedule based on agent's personality and knowledge
        if "teacher" in agent_state.agent_id.lower():
            # Teachers follow the teaching schedule
            for period in ["morning_1", "morning_2", "afternoon_1", "afternoon_2", "evening"]:
                if period in total_schedule.get("teaching_hours", {}):
                    schedule_parts.append(f"{period}: Teaching {total_schedule['teaching_hours'][period]}")
                else:
                    schedule_parts.append(f"{period}: Office hours")
        else:
            # Students follow the class schedule
            for period in ["morning_1", "morning_2", "afternoon_1", "afternoon_2", "evening"]:
                if period in total_schedule.get("student_activities", {}):
                    activity = total_schedule["student_activities"][period]
                    schedule_parts.append(f"{period}: {activity}")
                else:
                    schedule_parts.append(f"{period}: Free time")
        
        return f"Today's schedule: {'; '.join(schedule_parts)}"


class MovementTool(BaseTool):
    name = "movement_tool"
    description = "Tool for agent to move to a specific location"

    def __init__(self, world_manager):
        super().__init__()
        self.world_manager = world_manager

    def _run(self, target_location: str, agent_id: str) -> str:
        # Move agent to specified location
        self.world_manager.move_agent(agent_id, target_location)
        return f"Moved to {target_location}"


class BattleTool(BaseTool):
    name = "battle_tool"
    description = "Tool for agent to engage in a turn-based battle"

    def _run(self, opponent_id: str, agent_id: str) -> str:
        # Simulate a simple battle
        agent_hp = 100
        opponent_hp = 100
        
        battle_log = [f"Battle started between {agent_id} and {opponent_id}"]
        
        while agent_hp > 0 and opponent_hp > 0:
            # Simple turn-based battle
            damage_to_opponent = random.randint(10, 30)
            damage_to_agent = random.randint(10, 30)
            
            opponent_hp -= damage_to_opponent
            agent_hp -= damage_to_agent
            
            battle_log.append(f"{agent_id} dealt {damage_to_opponent} damage to {opponent_id}. {opponent_id} HP: {max(0, opponent_hp)}")
            battle_log.append(f"{opponent_id} dealt {damage_to_agent} damage to {agent_id}. {agent_id} HP: {max(0, agent_hp)}")
            
            if opponent_hp <= 0:
                battle_log.append(f"{agent_id} wins!")
                break
            elif agent_hp <= 0:
                battle_log.append(f"{opponent_id} wins!")
                break
        
        return f"Battle result: {'; '.join(battle_log)}"


class DialogueTool(BaseTool):
    name = "dialogue_tool"
    description = "Tool for agent to engage in dialogue with other agents"

    def __init__(self, world_manager):
        super().__init__()
        self.world_manager = world_manager

    def _run(self, participants: List[str], topic: str, agent_id: str) -> str:
        # Simulate a multi-turn dialogue
        dialogue_history = []
        max_rounds = config.CONFIG["max_dialogue_rounds"]
        
        for round_num in range(max_rounds):
            for participant in participants:
                # Each participant takes a turn to speak
                response = f"{participant} says something about {topic} (turn {round_num + 1})"
                dialogue_history.append(response)
                
                # Random chance to end dialogue early
                if random.random() < 0.1:
                    break
        
        return f"Dialogue about '{topic}' with {', '.join(participants)}: {'; '.join(dialogue_history)}"


class AgentNode:
    def __init__(self, agent_config: Dict[str, Any], world_manager, memory_manager, knowledge_base=None):
        self.agent_id = agent_config["id"]
        self.personality = agent_config["personality"]
        self.is_expert = agent_config["is_expert"]
        self.knowledge_base = knowledge_base
        self.world_manager = world_manager
        self.memory_manager = memory_manager
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
        # Create tools
        self.schedule_tool = ScheduleTool()
        self.movement_tool = MovementTool(world_manager)
        self.battle_tool = BattleTool()
        self.dialogue_tool = DialogueTool(world_manager)
        
        # Tool node
        self.tool_node = ToolNode(tools=[
            self.schedule_tool,
            self.movement_tool,
            self.battle_tool,
            self.dialogue_tool
        ])
    
    def get_current_state(self, day: int, time_period: str, location: str) -> AgentState:
        # Retrieve agent's memories from memory manager
        recent_memories = self.memory_manager.search_memories(query=f"day_{day}", agent_id=self.agent_id, limit=5)
        long_term_memories = self.memory_manager.search_memories(query="long_term", agent_id=self.agent_id, limit=10)
        
        return AgentState(
            agent_id=self.agent_id,
            day=day,
            time_period=time_period,
            location=location,
            personality=self.personality,
            schedule=[],
            memory=[m["content"] for m in recent_memories],
            dialogue_memory=[],
            long_term_memory=[m for m in long_term_memories],
            knowledge_access=self.is_expert,
            dialogue_requests=[],
            position=location
        )
    
    async def plan_daily_schedule(self, state: AgentState) -> AgentState:
        """Plan the agent's daily schedule based on persona, memories, and world state"""
        # Use LangChain to generate a personalized schedule
        prompt = f"""
        Based on the following information, create a daily schedule for {state.agent_id}:
        Personality: {state.personality}
        Current memories: {state.memory[:3]}
        Time period: {state.time_period}
        
        Return a structured schedule for the day.
        """
        
        # For simplicity, we'll use the schedule tool
        schedule_result = self.schedule_tool._run(state)
        state.current_action = "schedule_planning"
        state.action_result = schedule_result
        state.schedule = schedule_result.split("; ")
        
        # Store in memory
        self.memory_manager.add_memory({
            "agent_id": state.agent_id,
            "day": state.day,
            "time_period": state.time_period,
            "content": f"Planned schedule: {schedule_result}",
            "type": "daily_plan"
        })
        
        return state
    
    async def execute_action(self, state: AgentState) -> AgentState:
        """Execute the planned action"""
        # Determine what action to take based on schedule and current situation
        current_schedule_item = state.schedule[0] if state.schedule else f"{state.time_period}: Free time"
        
        if "teaching" in current_schedule_item.lower() and self.is_expert:
            # Teacher conducts lesson
            action = f"Teaching {current_schedule_item}"
            state.current_action = "teaching"
            state.action_result = f"Conducted lesson on {current_schedule_item}"
            
            # Add to memory
            self.memory_manager.add_memory({
                "agent_id": state.agent_id,
                "day": state.day,
                "time_period": state.time_period,
                "content": f"Taught {current_schedule_item}",
                "type": "action"
            })
        elif "class" in current_schedule_item.lower() or "study" in current_schedule_item.lower():
            # Student attends class
            action = f"Attending {current_schedule_item}"
            state.current_action = "studying"
            state.action_result = f"Attended {current_schedule_item}"
            
            # Add to memory
            self.memory_manager.add_memory({
                "agent_id": state.agent_id,
                "day": state.day,
                "time_period": state.time_period,
                "content": f"Attended {current_schedule_item}",
                "type": "action"
            })
        else:
            # Other activities
            action = f"Doing {current_schedule_item}"
            state.current_action = "other_activity"
            state.action_result = f"Performed {current_schedule_item}"
            
            # Add to memory
            self.memory_manager.add_memory({
                "agent_id": state.agent_id,
                "day": state.day,
                "time_period": state.time_period,
                "content": f"Performed {current_schedule_item}",
                "type": "action"
            })
        
        return state
    
    async def interact_with_world(self, state: AgentState) -> AgentState:
        """Interact with other agents and the world"""
        # Check if there are other agents in the same location
        other_agents = self.world_manager.get_agents_at_location(state.location)
        other_agents = [agent for agent in other_agents if agent != state.agent_id]
        
        if other_agents and random.random() < 0.7:  # 70% chance to interact
            # Engage in dialogue with other agents
            topic_options = [
                "today's activities",
                "recent learnings", 
                "upcoming plans",
                "knowledge sharing"
            ]
            chosen_topic = random.choice(topic_options)
            
            dialogue_result = self.dialogue_tool._run(other_agents, chosen_topic, state.agent_id)
            state.current_action = "dialogue"
            state.action_result = dialogue_result
            
            # Add to memory
            self.memory_manager.add_memory({
                "agent_id": state.agent_id,
                "day": state.day,
                "time_period": state.time_period,
                "content": f"Dialogued with {other_agents} about {chosen_topic}: {dialogue_result}",
                "type": "interaction"
            })
        else:
            # No interaction, continue with individual activities
            state.current_action = "independent_activity"
            state.action_result = f"Continued with independent activities in {state.location}"
            
            # Add to memory
            self.memory_manager.add_memory({
                "agent_id": state.agent_id,
                "day": state.day,
                "time_period": state.time_period,
                "content": f"Engaged in independent activities in {state.location}",
                "type": "action"
            })
        
        return state
    
    async def battle_if_appropriate(self, state: AgentState) -> AgentState:
        """Engage in battle if appropriate"""
        if random.random() < 0.2:  # 20% chance to battle
            # Check if there are other agents in the same location to battle
            other_agents = self.world_manager.get_agents_at_location(state.location)
            other_agents = [agent for agent in other_agents if agent != state.agent_id]
            
            if other_agents:
                opponent = random.choice(other_agents)
                battle_result = self.battle_tool._run(opponent, state.agent_id)
                
                state.current_action = "battle"
                state.action_result = battle_result
                state.battle_result = {"opponent": opponent, "result": battle_result}
                
                # Add battle result as a long-term memory
                self.memory_manager.add_memory({
                    "agent_id": state.agent_id,
                    "day": state.day,
                    "time_period": state.time_period,
                    "content": f"Battle with {opponent}: {battle_result}",
                    "type": "battle_memory"
                })
        
        return state
    
    async def update_long_term_memory(self, state: AgentState) -> AgentState:
        """Generate and store long-term memories"""
        # Create a summary of the current time period
        summary_content = f"Day {state.day}, {state.time_period}: Performed {state.current_action}. Result: {state.action_result}"
        
        # Add to long-term memory
        self.memory_manager.add_memory({
            "agent_id": state.agent_id,
            "day": state.day,
            "time_period": state.time_period,
            "content": summary_content,
            "type": "long_term_summary"
        })
        
        # Update state with latest memories
        recent_memories = self.memory_manager.search_memories(
            query=f"day_{state.day}", 
            agent_id=state.agent_id, 
            limit=5
        )
        state.memory = [m["content"] for m in recent_memories]
        
        return state


def create_agent_graph(agent_node: AgentNode):
    """Create a LangGraph for the agent"""
    # Define a graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("plan_schedule", agent_node.plan_daily_schedule)
    workflow.add_node("execute_action", agent_node.execute_action)
    workflow.add_node("interact_with_world", agent_node.interact_with_world)
    workflow.add_node("battle_if_appropriate", agent_node.battle_if_appropriate)
    workflow.add_node("update_memory", agent_node.update_long_term_memory)
    
    # Define edges
    workflow.add_edge("plan_schedule", "execute_action")
    workflow.add_edge("execute_action", "interact_with_world")
    workflow.add_edge("interact_with_world", "battle_if_appropriate")
    workflow.add_edge("battle_if_appropriate", "update_memory")
    
    # Set entry point
    workflow.set_entry_point("plan_schedule")
    
    # Compile the graph
    return workflow.compile()


class AgentManager:
    def __init__(self, world_manager, memory_manager, knowledge_base):
        self.agents = {}
        self.world_manager = world_manager
        self.memory_manager = memory_manager
        self.knowledge_base = knowledge_base
        self.graphs = {}
        
        # Load agent configurations
        for agent_id in config.AGENT_CONFIGS:
            agent_config = config.AGENT_CONFIGS[agent_id]
            agent_node = AgentNode(
                agent_config, 
                world_manager, 
                memory_manager, 
                knowledge_base if agent_config["is_expert"] else None
            )
            self.agents[agent_id] = agent_node
            self.graphs[agent_id] = create_agent_graph(agent_node)
    
    async def run_agent_step(self, agent_id: str, day: int, time_period: str, location: str):
        """Run one step for a specific agent"""
        initial_state = self.agents[agent_id].get_current_state(day, time_period, location)
        
        # Run the agent's graph
        result = await self.graphs[agent_id].ainvoke(initial_state)
        
        return result
    
    async def run_all_agents(self, day: int, time_period: str):
        """Run all agents for a specific time period"""
        tasks = []
        for agent_id in self.agents:
            location = self.world_manager.get_agent_location(agent_id)
            task = self.run_agent_step(agent_id, day, time_period, location)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Process results and update world state
        for i, agent_id in enumerate(self.agents):
            result = results[i]
            # Update agent's position if they moved
            if result.position != self.world_manager.get_agent_location(agent_id):
                self.world_manager.move_agent(agent_id, result.position)
        
        return dict(zip(self.agents.keys(), results))