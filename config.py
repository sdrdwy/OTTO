import json
import os

# Load configuration from JSON files
def load_config():
    # Load main config
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "simulation_days": 5,
            "max_dialogue_rounds": 3,
            "agent_count": 5,
            "locations": ["classroom", "library", "cafeteria", "playground", "office"]
        }
    
    # Load agent configurations
    agent_configs = {}
    agent_names = ["teacher", "student_1", "student_2", "student_3", "student_4"]
    
    for name in agent_names:
        config_file = f"{name}.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                agent_configs[name] = json.load(f)
        else:
            # Default agent configuration
            if name == "teacher":
                agent_configs[name] = {
                    "id": name,
                    "personality": "Knowledgeable and patient educator who explains concepts clearly",
                    "is_expert": True,
                    "dialogue_style": "instructive and encouraging",
                    "schedule_preferences": ["teaching", "office_hours"],
                    "habits": ["prepares lessons", "reviews student progress"]
                }
            else:
                agent_configs[name] = {
                    "id": name,
                    "personality": f"Student with unique learning style and curiosity about the world",
                    "is_expert": False,
                    "dialogue_style": "inquiring and collaborative",
                    "schedule_preferences": ["attending_classes", "studying", "socializing"],
                    "habits": ["asks questions", "takes notes", "works on assignments"]
                }
    
    # Load total schedule
    if os.path.exists('total_schedule.json'):
        with open('total_schedule.json', 'r', encoding='utf-8') as f:
            total_schedule = json.load(f)
    else:
        # Default schedule
        total_schedule = {
            "teaching_hours": {
                "morning_1": "Mathematics fundamentals",
                "morning_2": "Algebra concepts", 
                "afternoon_1": "Geometry basics",
                "afternoon_2": "Problem solving",
                "evening": "Review and office hours"
            },
            "student_activities": {
                "morning_1": "Mathematics class",
                "morning_2": "Algebra class",
                "afternoon_1": "Geometry class", 
                "afternoon_2": "Study group",
                "evening": "Homework and review"
            },
            "special_dates": {}
        }
    
    # Load map information
    if os.path.exists('map.json'):
        with open('map.json', 'r', encoding='utf-8') as f:
            map_info = json.load(f)
    else:
        # Default map
        map_info = {
            "classroom": {
                "description": "Main teaching area with desks and whiteboard",
                "function": "conducting lessons and classes"
            },
            "library": {
                "description": "Quiet area with books and study materials", 
                "function": "independent study and research"
            },
            "cafeteria": {
                "description": "Dining area for meals and socializing",
                "function": "eating and casual conversations"
            },
            "playground": {
                "description": "Outdoor area for physical activities",
                "function": "recreation and exercise"
            },
            "office": {
                "description": "Administrative area with faculty desks",
                "function": "meetings and office hours"
            }
        }
    
    return config, agent_configs, total_schedule, map_info

CONFIG, AGENT_CONFIGS, TOTAL_SCHEDULE, MAP_INFO = load_config()