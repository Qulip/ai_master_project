from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class MCPContext:
    """
    Model Context Protocol을 구현한 클래스.
    사용자의 목표, 태스크, 일정 등 컨텍스트를 유지합니다.
    """
    
    def __init__(self):
        self.goal: str = ""
        self.task_areas: List[str] = []
        self.todos: Dict[str, List[Dict[str, Any]]] = {}
        self.schedule: Dict[str, Any] = {
            "start_date": None,
            "end_date": None,
            "tasks": []
        }
        self.user_preferences: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []
        
    def set_goal(self, goal: str) -> None:
        """사용자의 목표를 설정합니다."""
        self.goal = goal
        self.add_to_history("user", f"목표 설정: {goal}")
        
    def set_task_areas(self, areas: List[str]) -> None:
        """태스크 영역을 설정합니다."""
        self.task_areas = areas
        self.add_to_history("system", f"태스크 영역 설정: {', '.join(areas)}")
        
    def add_todo(self, area: str, task: Dict[str, Any]) -> None:
        """특정 영역에 할 일을 추가합니다."""
        if area not in self.todos:
            self.todos[area] = []
        self.todos[area].append(task)
        self.add_to_history("system", f"할 일 추가 ({area}): {task['title']}")
        
    def set_schedule(self, start_date: datetime, tasks: List[Dict[str, Any]]) -> None:
        """일정을 설정합니다."""
        total_days = sum(task.get("duration_days", 0) for task in tasks)
        end_date = start_date + timedelta(days=total_days)
        
        self.schedule = {
            "start_date": start_date,
            "end_date": end_date,
            "tasks": tasks
        }
        self.add_to_history("system", f"일정 설정: {start_date.strftime('%Y-%m-%d')}부터 {end_date.strftime('%Y-%m-%d')}까지")
        
    def update_user_preference(self, key: str, value: Any) -> None:
        """사용자 선호도를 업데이트합니다."""
        self.user_preferences[key] = value
        self.add_to_history("user", f"선호도 업데이트: {key}={value}")
        
    def add_to_history(self, role: str, message: str) -> None:
        """대화 기록에 메시지를 추가합니다."""
        self.conversation_history.append({
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_context_dict(self) -> Dict[str, Any]:
        """전체 컨텍스트를 딕셔너리로 반환합니다."""
        return {
            "goal": self.goal,
            "task_areas": self.task_areas,
            "todos": self.todos,
            "schedule": self.schedule,
            "user_preferences": self.user_preferences,
            "conversation_history": self.conversation_history[-5:] if self.conversation_history else []  # 최근 5개 대화만 포함
        }
        
    def get_formatted_todos(self) -> str:
        """할 일 목록을 마크다운 형식으로 반환합니다."""
        if not self.todos:
            return "할 일이 없습니다."
            
        result = []
        for area, tasks in self.todos.items():
            result.append(f"### {area}")
            for task in tasks:
                duration = f" ({task.get('duration_days', 0)}일)" if 'duration_days' in task else ""
                result.append(f"- [ ] {task['title']}{duration}")
            result.append("")
        
        return "\n".join(result)
        
    def get_formatted_schedule(self) -> str:
        """일정을 마크다운 형식으로 반환합니다."""
        if not self.schedule["start_date"]:
            return "일정이 없습니다."
            
        result = ["### 추천 일정"]
        result.append(f"- 시작일: {self.schedule['start_date'].strftime('%Y-%m-%d')}")
        result.append(f"- 완료일: {self.schedule['end_date'].strftime('%Y-%m-%d')}")
        result.append("")
        
        current_date = self.schedule["start_date"]
        for task in self.schedule["tasks"]:
            end_date = current_date + timedelta(days=task.get("duration_days", 0) - 1)
            result.append(f"- {current_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}: {task['title']}")
            current_date = end_date + timedelta(days=1)
            
        return "\n".join(result) 