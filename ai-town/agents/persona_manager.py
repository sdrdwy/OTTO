"""
Persona Manager System
Handles loading, saving, and managing different agent personalities
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class PersonaManager:
    def __init__(self, persona_dir: str = "personas"):
        self.persona_dir = Path(persona_dir)
        self.personas = {}
        self.load_all_personas()
    
    def load_all_personas(self):
        """Load all persona files from the personas directory"""
        if not self.persona_dir.exists():
            print(f"Persona directory {self.persona_dir} does not exist")
            return
        
        for file_path in self.persona_dir.glob("*.json"):
            self.load_personas_from_file(file_path)
    
    def load_personas_from_file(self, file_path: Path):
        """Load personas from a specific JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_personas = json.load(f)
                self.personas.update(file_personas)
                print(f"Loaded {len(file_personas)} personas from {file_path.name}")
        except Exception as e:
            print(f"Error loading personas from {file_path}: {e}")
    
    def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific persona by ID"""
        return self.personas.get(persona_id)
    
    def list_personas(self, role: str = None) -> list:
        """List all personas, optionally filtered by role"""
        if role:
            return [pid for pid, pdata in self.personas.items() if pdata.get('role') == role]
        return list(self.personas.keys())
    
    def add_persona(self, persona_id: str, persona_data: Dict[str, Any]):
        """Add or update a persona"""
        self.personas[persona_id] = persona_data
    
    def save_persona_to_file(self, persona_id: str, file_path: str = None):
        """Save a specific persona to a JSON file"""
        if persona_id not in self.personas:
            print(f"Persona {persona_id} does not exist")
            return False
        
        if file_path is None:
            file_path = f"{self.persona_dir}/{persona_id}.json"
        
        # Load existing data or create new dict
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Update with the specific persona
        data[persona_id] = self.personas[persona_id]
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved persona {persona_id} to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving persona {persona_id} to {file_path}: {e}")
            return False
    
    def save_all_personas(self):
        """Save all personas to their respective files"""
        # Group personas by role to save them to appropriate files
        role_based_personas = {}
        for persona_id, persona_data in self.personas.items():
            role = persona_data.get('role', 'unknown')
            if role not in role_based_personas:
                role_based_personas[role] = {}
            role_based_personas[role][persona_id] = persona_data
        
        for role, personas in role_based_personas.items():
            file_path = f"{self.persona_dir}/{role.lower()}_personas.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(personas, f, ensure_ascii=False, indent=2)
                print(f"Saved {len(personas)} {role} personas to {file_path}")
            except Exception as e:
                print(f"Error saving {role} personas to {file_path}: {e}")


# Global persona manager instance
persona_manager = PersonaManager()