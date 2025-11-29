"""
Daily Schedule functionality for AI Town
Manages personal daily schedules for agents divided into 5 time periods
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os


class DailySchedule:
    def __init__(self, agent_name: str, calendar_file: str = "calendar.json"):
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
        
    def create_daily_schedule(self, date: str, fixed_classes: List[Dict] = None):
        """
        根据公共calendar创建当天的个人日程
        时间段划分：上午上课、上午自由活动、下午上课、下午自由活动、晚上
        """
        if fixed_classes is None:
            fixed_classes = []
            
        # 初始化当天日程
        self.personal_calendar[date] = {
            "date": date,
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
        
        # 为自由活动时间段生成活动
        self._generate_free_time_activities(date)
        
        return self.personal_calendar[date]
    
    def _generate_free_time_activities(self, date: str):
        """为自由活动时间段生成活动"""
        # 生成上午自由活动
        if not self.personal_calendar[date]["morning_free"]:
            self.personal_calendar[date]["morning_free"] = [
                {
                    "activity": "personal study",
                    "location": "library",
                    "preferences": ["study", "focus"]
                }
            ]
        
        # 生成下午自由活动
        if not self.personal_calendar[date]["afternoon_free"]:
            self.personal_calendar[date]["afternoon_free"] = [
                {
                    "activity": "social activity",
                    "location": "park",
                    "preferences": ["relax", "socialize"]
                }
            ]
        
        # 生成晚上活动
        if not self.personal_calendar[date]["evening"]:
            self.personal_calendar[date]["evening"] = [
                {
                    "activity": "rest",
                    "location": "home",
                    "preferences": ["rest", "sleep"]
                }
            ]
    
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
            filename = f"schedule_{self.agent_name}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.personal_calendar, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving schedule: {e}")
    
    def load_schedule(self, filename: str = None):
        """从文件加载个人日程"""
        if filename is None:
            filename = f"schedule_{self.agent_name}.json"
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.personal_calendar = json.load(f)
            except Exception as e:
                print(f"Error loading schedule: {e}")
                self.personal_calendar = {}
        else:
            self.personal_calendar = {}