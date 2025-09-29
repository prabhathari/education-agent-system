from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.orchestrator import OrchestratorAgent, AgentState
from app.models import LearningRequest, QuizAnswer, ProgressRequest
from app.agents.quiz_agent import QuizAgent
import uuid

app = FastAPI(title="Education Multi-Agent System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Request/Response Models
# class LearningRequest(BaseModel):
#     user_id: Optional[str] = None
#     topic: str
#     learning_goal: str
#     current_level: Optional[int] = 0

# class QuizAnswer(BaseModel):
#     user_id: str
#     answer: str

# class ProgressRequest(BaseModel):
#     user_id: str

# In-memory session storage (use Redis in production)
sessions: Dict[str, AgentState] = {}


@app.post("/start_learning")
async def start_learning(request: LearningRequest):
    """Initialize a new learning session"""
    user_id = request.user_id or str(uuid.uuid4())
    
    initial_state: AgentState = {
        "user_id": user_id,
        "current_topic": request.topic,
        "learning_goal": request.learning_goal,
        "conversation_history": [],
        "quiz_results": [],
        "current_understanding_level": float(request.current_level),
        "next_action": "analyze",
        "agent_outputs": {},
        "materials_found": []
    }
    
    # Run orchestrator
    result = await orchestrator.run(initial_state)
    
    # Store session
    sessions[user_id] = result
    
    return {
        "user_id": user_id,
        "status": "Learning session started",
        "initial_action": result.get("next_action"),
        "explanation": result.get("agent_outputs", {}).get("tutor_explanation"),
        "quiz": result.get("agent_outputs", {}).get("current_quiz"),
        "materials": result.get("materials_found", [])
    }

# @app.post("/submit_answer")
# async def submit_answer(answer: QuizAnswer):
#     """Submit quiz answer and get feedback"""
#     if answer.user_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session not found")
    
#     state = sessions[answer.user_id]
    
#     # Evaluate answer
#     quiz_agent = orchestrator.quiz
#     state = await quiz_agent.evaluate_answer(state, answer.answer)
    
#     # Continue learning flow
#     result = await orchestrator.run(state)
#     sessions[answer.user_id] = result
    
#     return {
#         "evaluation": state["quiz_results"][-1] if state["quiz_results"] else None,
#         "new_understanding_level": state["current_understanding_level"],
#         "next_action": result.get("next_action"),
#         "next_content": result.get("agent_outputs")
#     }
# @app.post("/submit_answer")
# async def submit_answer(answer: QuizAnswer):
#     """Submit quiz answer and get feedback"""
#     if answer.user_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session not found")
    
#     state = sessions[answer.user_id]
    
#     # Simple evaluation for now
#     quiz = state.get("agent_outputs", {}).get("current_quiz", {})
#     correct = False
    
#     if quiz.get("correct_answer"):
#         correct = answer.answer == quiz["correct_answer"]
    
#     feedback = {
#         "correct": correct,
#         "score": 10 if correct else 0,
#         "feedback": quiz.get("explanation", "Good try!"),
#         "misconceptions": []
#     }
    
#     state["quiz_results"].append(feedback)
    
#     # Update understanding
#     if correct:
#         state["current_understanding_level"] = min(10, state["current_understanding_level"] + 0.5)
    
#     # Generate a new quiz
#     quiz_prompt = f"""
#     Create a NEW multiple choice question about {state['current_topic']}.
#     Make it slightly harder than before.
#     Return ONLY valid JSON:
#     {{
#         "question": "Different question",
#         "options": ["A) Option", "B) Option", "C) Option", "D) Option"],
#         "correct_answer": "A",
#         "explanation": "Why this is correct"
#     }}
#     """
    
#     try:
#         quiz_response = await orchestrator.llm.generate(quiz_prompt)
#         # Clean JSON
#         if "```json" in quiz_response:
#             quiz_response = quiz_response.split("```json")[1].split("```")[0]
#         import json
#         new_quiz = json.loads(quiz_response.strip())
#         state["agent_outputs"]["current_quiz"] = new_quiz
#     except:
#         pass
    
#     sessions[answer.user_id] = state
    
#     return {
#         "evaluation": feedback,
#         "new_understanding_level": state["current_understanding_level"],
#         "next_action": "quiz",
#         "next_content": state.get("agent_outputs")
#     }
# @app.post("/submit_answer")
# async def submit_answer(answer: QuizAnswer):
#     """Submit quiz answer and get feedback"""
#     if answer.user_id not in sessions:
#         raise HTTPException(status_code=404, detail="Session not found")
    
#     state = sessions[answer.user_id]
    
#     # Use the quiz agent to evaluate
#     quiz_agent = QuizAgent()  # Create instance
#     state = await quiz_agent.evaluate_answer(state, answer.answer)
    
#     # Get the latest feedback
#     latest_feedback = state["quiz_results"][-1] if state["quiz_results"] else None
    
#     # Store updated session
#     sessions[answer.user_id] = state
    
#     return {
#         "evaluation": latest_feedback,
#         "new_understanding_level": state["current_understanding_level"],
#         "next_action": "quiz",
#         "next_content": {
#             "current_quiz": state.get("agent_outputs", {}).get("current_quiz"),
#             "tutor_explanation": None  # Don't send new explanation unless needed
#         }
#     }

@app.post("/submit_answer")
async def submit_answer(answer: QuizAnswer):
    """Submit quiz answer and get feedback"""
    if answer.user_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[answer.user_id]
    
    # Use the quiz agent for evaluation (the proper agent way)
    from app.agents.quiz_agent import QuizAgent
    quiz_agent = QuizAgent()
    
    # Evaluate the answer
    state = await quiz_agent.evaluate_answer(state, answer.answer)
    
    # The quiz agent should have added feedback to quiz_results
    latest_feedback = state["quiz_results"][-1] if state.get("quiz_results") else None
    
    # Make sure we have feedback
    if not latest_feedback:
        # Fallback if quiz agent didn't work
        current_quiz = state.get("agent_outputs", {}).get("current_quiz", {})
        correct_answer = current_quiz.get("correct_answer", "")
        
        # Simple comparison
        user_answer = answer.answer
        if user_answer.startswith(('A)', 'B)', 'C)', 'D)')):
            user_answer = user_answer[0]
        
        is_correct = (user_answer == correct_answer)
        
        latest_feedback = {
            "correct": is_correct,
            "score": 10 if is_correct else 0,
            "feedback": f"{'Correct!' if is_correct else 'Wrong.'} The answer was {correct_answer}. {current_quiz.get('explanation', '')}",
            "misconceptions": []
        }
    
    # Save updated state
    sessions[answer.user_id] = state
    
    # Return the complete response structure
    return {
        "evaluation": latest_feedback,  # This MUST be here for frontend
        "new_understanding_level": state["current_understanding_level"],
        "next_action": "quiz",
        "next_content": {
            "current_quiz": state.get("agent_outputs", {}).get("current_quiz"),
            "tutor_explanation": None
        }
    }

@app.get("/progress/{user_id}")
async def get_progress(user_id: str):
    """Get learning progress for a user"""
    if user_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[user_id]
    
    return {
        "user_id": user_id,
        "topic": state["current_topic"],
        "understanding_level": state["current_understanding_level"],
        "quiz_count": len(state["quiz_results"]),
        "materials_reviewed": len(state["materials_found"]),
        "progress_analysis": state.get("agent_outputs", {}).get("progress")
    }

@app.post("/get_help/{user_id}")
async def get_help(user_id: str):
    """Get additional explanation when stuck"""
    if user_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[user_id]
    state["next_action"] = "tutor"  # Force tutor explanation
    
    result = await orchestrator.run(state)
    sessions[user_id] = result
    
    return {
        "explanation": result.get("agent_outputs", {}).get("tutor_explanation"),
        "materials": result.get("materials_found", [])
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Education API is running", "docs_url": "/docs"}

@app.post("/refresh_materials/{user_id}")
async def refresh_materials(user_id: str):
    """Get new learning materials based on current progress"""
    if user_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[user_id]
    
    # Use research agent to find new materials
    from app.agents.research_agent import ResearchAgent
    research_agent = ResearchAgent()
    state = await research_agent.find_materials(state)
    
    sessions[user_id] = state
    
    return {
        "materials": state.get("materials_found", []),
        "understanding_level": state["current_understanding_level"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)