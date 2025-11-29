"""
Daily Schedule functionality for AI Town
Manages personal daily schedules for agents divided into 5 time periods
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
import random


class DailySchedule:
    def __init__(self, agent_name: str, calendar_file: str = "config_files/system_configs/calendar.json"):
        self.agent_name = agent_name
        self.calendar_file = calendar_file
        self.personal_calendar = {}
        self.time_periods = [
            "morning_class",      # 上午固定上课
            "morning_free",       # 上午自由活动
            "afternoon_class",    # 下午固定上课
            "afternoon_free",     # 下午自由活动
            "evening"             # 晚上
        ]
        
    def create_daily_schedule(self, date: str, fixed_classes: List[Dict] = None, agent_preferences: Dict = None, memory_context: List[Dict] = None):
        """
        智能创建当天的个人日程
        时间段划分：上午上课、上午自由活动、下午上课、下午自由活动、晚上
        现在会根据代理的偏好、目标和记忆智能规划
        """
        if fixed_classes is None:
            fixed_classes = []
        if agent_preferences is None:
            agent_preferences = {
                "learning_goals": ["study", "improve skills"],
                "preferred_locations": ["library", "classroom"],
                "social_preferences": ["collaborate", "network"],
                "activity_preferences": ["study", "practice", "discuss"]
            }
        if memory_context is None:
            memory_context = []
            
        # 初始化当天日程
        self.personal_calendar[date] = {
            "date": date,
            "agent_name": self.agent_name,
            "morning_class": [],      # 上午固定上课
            "morning_free": [],       # 上午自由活动
            "afternoon_class": [],    # 下午固定上课
            "afternoon_free": [],     # 下午自由活动
            "evening": []             # 晚上
        }
        
        # 添加固定课程到对应的上课时间段
        for class_event in fixed_classes:
            if "morning" in class_event.get("time_period", ""):
                self.personal_calendar[date]["morning_class"].append(class_event)
            elif "afternoon" in class_event.get("time_period", ""):
                self.personal_calendar[date]["afternoon_class"].append(class_event)
        
        # 智能生成自由活动时间段的活动，基于代理偏好和记忆
        self._generate_intelligent_free_time_activities(date, agent_preferences, memory_context)
        
        # 保存日程到独立的JSON文件
        self.save_schedule()
        
        return self.personal_calendar[date]
    
    def _generate_intelligent_free_time_activities(self, date: str, agent_preferences: Dict, memory_context: List[Dict] = None):
        """基于代理偏好和记忆智能生成自由活动"""
        if memory_context is None:
            memory_context = []
        
        # 根据学习目标和偏好生成上午自由活动
        if not self.personal_calendar[date]["morning_free"]:
            morning_activity = self._plan_activity_for_period(
                "morning", 
                agent_preferences,
                memory_context
            )
            self.personal_calendar[date]["morning_free"] = [morning_activity]
        
        # 根据学习目标和偏好生成下午自由活动
        if not self.personal_calendar[date]["afternoon_free"]:
            afternoon_activity = self._plan_activity_for_period(
                "afternoon", 
                agent_preferences,
                memory_context
            )
            self.personal_calendar[date]["afternoon_free"] = [afternoon_activity]
        
        # 生成晚上活动（通常为休息）
        if not self.personal_calendar[date]["evening"]:
            self.personal_calendar[date]["evening"] = [
                {
                    "activity": "rest and reflection",
                    "location": "home",
                    "preferences": ["rest", "sleep", "reflect on day"],
                    "memory_context": [mem["content"] for mem in memory_context[:3]] if memory_context else []  # Include top 3 memories for reflection
                }
            ]
    
    def _plan_activity_for_period(self, period: str, agent_preferences: Dict, memory_context: List[Dict] = None) -> Dict:
        """为特定时间段智能规划活动"""
        if memory_context is None:
            memory_context = []
        
        # 根据代理的学习目标和偏好选择活动
        learning_goals = agent_preferences.get("learning_goals", [])
        preferred_locations = agent_preferences.get("preferred_locations", ["library", "classroom"])
        activity_preferences = agent_preferences.get("activity_preferences", ["study", "practice"])
        social_preferences = agent_preferences.get("social_preferences", ["collaborate"])
        
        # 分析记忆上下文，以更好地规划活动
        relevant_topics = []
        if memory_context:
            # 从记忆中提取相关主题，用于规划更有意义的活动
            for memory in memory_context:
                if "content" in memory:
                    content = memory["content"].lower()
                    if "study" in content or "learn" in content:
                        relevant_topics.append("study")
                    elif "discuss" in content or "talk" in content:
                        relevant_topics.append("discussion")
                    elif "project" in content:
                        relevant_topics.append("project work")
                    elif "research" in content:
                        relevant_topics.append("research")
        
        # 智能选择活动类型
        if relevant_topics:
            # 如果有相关的记忆主题，优先考虑
            activity_type = random.choice(relevant_topics + activity_preferences)
        elif "study" in activity_preferences or "improve skills" in learning_goals:
            activity_type = random.choice(["study", "practice", "review", "research"])
        else:
            activity_type = random.choice(activity_preferences)
        
        # 智能选择地点
        location = random.choice(preferred_locations)
        
        # 构建活动详情
        activity_details = {
            "activity": f"{activity_type} related to {random.choice(learning_goals) if learning_goals else 'personal development'}",
            "location": location,
            "preferences": activity_preferences[:2] + learning_goals[:2],
            "planned_by": self.agent_name,
            "planning_timestamp": datetime.now().isoformat(),
            "memory_context_used": [mem.get("content", "")[:100] for mem in memory_context[:2]] if memory_context else []  # Include context used for planning
        }
        
        # 如果代理喜欢社交，可能添加协作活动
        if random.random() < 0.3 and social_preferences:  # 30% 概率添加社交活动
            activity_details["social_element"] = random.choice(social_preferences)
        
        return activity_details
    
    def get_schedule_for_period(self, date: str, period: str) -> List[Dict]:
        """获取特定日期特定时间段的安排"""
        if date not in self.personal_calendar:
            return []
        
        if period not in self.time_periods:
            return []
        
        return self.personal_calendar[date].get(period, [])
    
    def update_schedule_period(self, date: str, period: str, activities: List[Dict]):
        """更新特定日期特定时间段的安排"""
        if date not in self.personal_calendar:
            self.personal_calendar[date] = {
                "date": date,
                "agent_name": self.agent_name,
                "morning_class": [],
                "morning_free": [],
                "afternoon_class": [],
                "afternoon_free": [],
                "evening": []
            }
        
        if period in self.time_periods:
            self.personal_calendar[date][period] = activities
    
    def get_current_period_schedule(self, current_datetime: datetime = None) -> Dict:
        """获取当前时间段的安排"""
        if current_datetime is None:
            current_datetime = datetime.now()
        
        date_str = current_datetime.date().isoformat()
        hour = current_datetime.hour
        
        # 根据小时数确定当前时间段
        if 6 <= hour < 12:
            # 上午时段 - 需要进一步判断是上课还是自由活动
            if self.personal_calendar.get(date_str, {}).get("morning_class"):
                current_period = "morning_class"
            else:
                current_period = "morning_free"
        elif 12 <= hour < 18:
            # 下午时段 - 需要进一步判断是上课还是自由活动
            if self.personal_calendar.get(date_str, {}).get("afternoon_class"):
                current_period = "afternoon_class"
            else:
                current_period = "afternoon_free"
        else:
            # 晚上时段
            current_period = "evening"
        
        return {
            "date": date_str,
            "period": current_period,
            "schedule": self.get_schedule_for_period(date_str, current_period)
        }
    
    def add_activity_to_period(self, date: str, period: str, activity: Dict):
        """向特定时间段添加活动"""
        if date not in self.personal_calendar:
            self.create_daily_schedule(date)
        
        if period in self.time_periods:
            self.personal_calendar[date][period].append(activity)
    
    def get_full_daily_schedule(self, date: str) -> Dict:
        """获取完整的一天安排"""
        if date not in self.personal_calendar:
            return {}
        return self.personal_calendar[date]
    
    def save_schedule(self, filename: str = None):
        """保存个人日程到文件"""
        if filename is None:
            filename = f"config_files/schedule_configs/schedule_{self.agent_name}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.personal_calendar, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving schedule: {e}")
    
    def load_schedule(self, filename: str = None):
        """从文件加载个人日程"""
        if filename is None:
            filename = f"config_files/schedule_configs/schedule_{self.agent_name}.json"
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.personal_calendar = json.load(f)
            except Exception as e:
                print(f"Error loading schedule: {e}")
                self.personal_calendar = {}
        else:
            self.personal_calendar = {}