from typing import Dict, Any
from datetime import datetime
import json
from app.tools.llm_client import LLMClient

class TrackerAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    async def update_progress(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze learning progress"""
        
        # Analyze progress
        prompt = f"""
        Analyze the student's learning progress:
        
        Topic: {state['current_topic']}
        Goal: {state['learning_goal']}
        Current Understanding: {state['current_understanding_level']}/10
        Quiz History: {len(state.get('quiz_results', []))} quizzes taken
        Materials Reviewed: {len(state.get('materials_found', []))}
        
        Provide:
        1. Progress percentage toward goal
        2. Strengths identified
        3. Areas needing improvement
        4. Recommended next steps
        
        Return as JSON.
        """
        
        analysis = await self.llm.generate(prompt)
        
        try:
            progress_data = json.loads(analysis)
        except:
            progress_data = {
                "progress_percentage": int(state['current_understanding_level'] * 10),
                "strengths": [],
                "improvements_needed": [],
                "next_steps": ["Continue learning"]
            }
        
        state['agent_outputs']['progress'] = progress_data
        
        # Log progress (in production, save to database)
        progress_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": state['user_id'],
            "topic": state['current_topic'],
            "understanding_level": state['current_understanding_level'],
            "quiz_performance": self._calculate_quiz_performance(state),
            **progress_data
        }
        
        # Here you would save to database
        print(f"Progress logged: {progress_entry}")
        
        return state
    
    def _calculate_quiz_performance(self, state: Dict[str, Any]) -> float:
        """Calculate average quiz performance"""
        quiz_results = state.get('quiz_results', [])
        if not quiz_results:
            return 0.0
        
        scores = [r.get('score', 0) for r in quiz_results[-5:]]  # Last 5 quizzes
        return sum(scores) / len(scores) if scores else 0.0