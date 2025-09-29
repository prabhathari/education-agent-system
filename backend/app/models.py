# backend/app/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LearningRequest(BaseModel):
    user_id: Optional[str] = None
    topic: str
    learning_goal: str
    current_level: Optional[int] = 0

class QuizAnswer(BaseModel):
    user_id: str
    answer: str

class ProgressRequest(BaseModel):
    user_id: str

class AgentState(BaseModel):
    user_id: str
    current_topic: str
    learning_goal: str
    conversation_history: List[Dict[str, str]] = []
    quiz_results: List[Dict[str, Any]] = []
    current_understanding_level: float = 0.0
    next_action: str = ""
    agent_outputs: Dict[str, Any] = {}
    materials_found: List[Dict[str, str]] = []