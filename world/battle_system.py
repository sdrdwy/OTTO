import random
from typing import Dict, Any, List, TYPE_CHECKING
if TYPE_CHECKING:
    from agents.agent_base import BaseAgent


class BattleSystem:
    def __init__(self):
        self.battle_log = []

    def initiate_battle(self, attacker: 'BaseAgent', defender: 'BaseAgent') -> Dict[str, Any]:
        """Initiate a battle between two agents."""
        # Simple turn-based battle system
        attacker_power = self.calculate_agent_power(attacker)
        defender_power = self.calculate_agent_power(defender)
        
        # Battle rounds
        battle_rounds = []
        attacker_hp = 100
        defender_hp = 100
        
        round_num = 1
        while attacker_hp > 0 and defender_hp > 0 and round_num <= 5:
            # Attacker attacks
            attack_damage = max(1, attacker_power + random.randint(-5, 5))
            defender_hp -= attack_damage
            battle_rounds.append({
                "round": round_num,
                "attacker": attacker.name,
                "defender": defender.name,
                "action": f"{attacker.name} attacks {defender.name} for {attack_damage} damage",
                "defender_hp": max(0, defender_hp)
            })
            
            if defender_hp <= 0:
                break
                
            # Defender attacks back
            defend_damage = max(1, defender_power + random.randint(-5, 5))
            attacker_hp -= defend_damage
            battle_rounds.append({
                "round": round_num,
                "attacker": defender.name,
                "defender": attacker.name,
                "action": f"{defender.name} attacks {attacker.name} for {defend_damage} damage",
                "defender_hp": max(0, attacker_hp)
            })
            
            round_num += 1
        
        # Determine winner
        if attacker_hp > defender_hp:
            winner = attacker.name
            loser = defender.name
        elif defender_hp > attacker_hp:
            winner = defender.name
            loser = attacker.name
        else:
            winner = "Draw"
            loser = "Draw"
        
        battle_result = {
            "winner": winner,
            "loser": loser,
            "attacker_final_hp": max(0, attacker_hp),
            "defender_final_hp": max(0, defender_hp),
            "total_rounds": round_num - 1,
            "battle_log": battle_rounds
        }
        
        # Add battle result to the battle log
        self.battle_log.append(battle_result)
        
        # Generate long-term memory for both agents
        battle_summary = f"Battled with {defender.name}. Result: {winner} won. Rounds: {round_num - 1}"
        attacker.generate_long_term_memory(battle_summary)
        defender.generate_long_term_memory(f"Battled with {attacker.name}. Result: {winner} won. Rounds: {round_num - 1}")
        
        return battle_result

    def calculate_agent_power(self, agent: 'BaseAgent') -> int:
        """Calculate agent's battle power based on personality and other factors."""
        # Base power
        base_power = 10
        
        # Adjust based on personality
        if "confident" in agent.personality.lower() or "competitive" in agent.personality.lower():
            base_power += 5
        elif "shy" in agent.personality.lower() or "quiet" in agent.personality.lower():
            base_power -= 3
        
        # Adjust based on schedule compliance (more disciplined agents might be stronger)
        # This is a placeholder - in a real system we'd track more stats
        base_power += random.randint(-2, 2)
        
        return max(1, base_power)  # Ensure power is at least 1