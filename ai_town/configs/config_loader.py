import json
import os
from typing import Dict, Any


class ConfigLoader:
    @staticmethod
    def load_config(config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file by name (without extension)
        """
        config_path = f"/workspace/ai_town/configs/{config_name}.json"
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    @staticmethod
    def load_all_agent_configs() -> Dict[str, Dict[str, Any]]:
        """
        Load all agent configuration files
        """
        agent_configs = {}
        
        # Define agent config files
        agent_files = ['teacher.json', 'student1.json', 'student2.json', 'student3.json', 'student4.json']
        
        for agent_file in agent_files:
            config_name = agent_file.replace('.json', '')
            try:
                agent_configs[config_name] = ConfigLoader.load_config(config_name)
            except FileNotFoundError:
                print(f"Warning: Agent config file {agent_file} not found")
                continue
        
        return agent_configs