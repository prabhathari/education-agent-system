from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Literal
from app.tools.llm_client import LLMClient
from app.agents.tutor_agent import TutorAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.research_agent import ResearchAgent
from app.agents.tracker_agent import TrackerAgent

class AgentState(TypedDict):
    user_id: str
    current_topic: str
    learning_goal: str
    conversation_history: List[Dict[str, str]]
    quiz_results: List[Dict[str, Any]]
    current_understanding_level: float
    next_action: str
    agent_outputs: Dict[str, Any]
    materials_found: List[Dict[str, str]]

class OrchestratorAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.tutor = TutorAgent()
        self.quiz = QuizAgent()
        self.research = ResearchAgent()
        self.tracker = TrackerAgent()
        
        # Build the state graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_state", self.analyze_state)
        workflow.add_node("tutor", self.tutor.explain_concept)
        workflow.add_node("quiz", self.quiz.generate_quiz)
        workflow.add_node("research", self.research.find_materials)
        workflow.add_node("track", self.tracker.update_progress)
        workflow.add_node("decide_next", self.decide_next_action)
        
        # Add edges
        workflow.set_entry_point("analyze_state")
        
        workflow.add_edge("analyze_state", "decide_next")
        
        # Conditional routing based on next_action
        workflow.add_conditional_edges(
            "decide_next",
            self.route_next_action,
            {
                "tutor": "tutor",
                "quiz": "quiz",
                "research": "research",
                "track": "track",
                "end": END
            }
        )
        
        # All agents lead back to track
        workflow.add_edge("tutor", "track")
        workflow.add_edge("quiz", "track")
        workflow.add_edge("research", "track")
        workflow.add_edge("track", "analyze_state")
        
        return workflow.compile()
    
    async def analyze_state(self, state: AgentState) -> AgentState:
        """Analyze current learning state and context"""
        prompt = f"""
        Analyze the student's current learning state:
        
        User ID: {state['user_id']}
        Topic: {state['current_topic']}
        Goal: {state['learning_goal']}
        Understanding Level: {state['current_understanding_level']}/10
        Recent Quiz Results: {state['quiz_results'][-3:] if state['quiz_results'] else 'None'}
        
        Based on this, what should be the focus? Identify any learning gaps.
        """
        
        analysis = await self.llm.generate(prompt)
        state['agent_outputs']['analysis'] = analysis
        return state
    
    async def decide_next_action(self, state: AgentState) -> AgentState:
        """Decide which agent to activate next"""
        prompt = f"""
        Based on the analysis: {state['agent_outputs'].get('analysis', '')}
        Understanding level: {state['current_understanding_level']}/10
        
        Choose the next action:
        - 'tutor': If concept explanation needed
        - 'quiz': If ready to test knowledge
        - 'research': If need additional materials
        - 'track': If only progress update needed
        - 'end': If learning goal achieved
        
        Return only one word: tutor, quiz, research, track, or end.
        """
        
        next_action = await self.llm.generate(prompt, temperature=0.3)
        state['next_action'] = next_action.strip().lower()
        return state
    
    def route_next_action(self, state: AgentState) -> Literal["tutor", "quiz", "research", "track", "end"]:
        """Route to next agent based on decision"""
        action = state.get('next_action', 'end')
        if action in ["tutor", "quiz", "research", "track", "end"]:
            return action
        return "end"
    
    # async def run(self, initial_state: AgentState) -> AgentState:
    #     """Execute the workflow"""
    #     result = await self.workflow.ainvoke(initial_state)
    #     return result
    # async def run(self, initial_state: AgentState) -> AgentState:
    #     """Execute a simple workflow"""
    #     # Just do one explanation for now
    #     state = initial_state
        
    #     # Generate a simple explanation
    #     prompt = f"Explain {state['current_topic']} in simple terms."
    #     explanation = await self.llm.generate(prompt)
        
    #     state['agent_outputs']['tutor_explanation'] = explanation
    #     state['current_understanding_level'] = 5.0
        
    #     return state
    async def run(self, initial_state: AgentState) -> AgentState:
        """Execute a simple workflow"""
        state = initial_state
        
        # Generate explanation
        explanation_prompt = f"Explain {state['current_topic']} in simple terms for someone at level {state['current_understanding_level']}/10."
        explanation = await self.llm.generate(explanation_prompt)
        state['agent_outputs']['tutor_explanation'] = explanation
        
        # Generate a quiz question
        quiz_prompt = f"""
        Create a multiple choice question about {state['current_topic']}.
        Return ONLY valid JSON in this format:
        {{
            "question": "Your question here",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct_answer": "A",
            "explanation": "Brief explanation"
        }}
        """
        
        try:
            quiz_response = await self.llm.generate(quiz_prompt, temperature=0.5)
            # Clean the response
            quiz_response = quiz_response.strip()
            if quiz_response.startswith("```json"):
                quiz_response = quiz_response[7:]
            if quiz_response.startswith("```"):
                quiz_response = quiz_response[3:]
            if quiz_response.endswith("```"):
                quiz_response = quiz_response[:-3]
            
            import json
            quiz_data = json.loads(quiz_response.strip())
            state['agent_outputs']['current_quiz'] = quiz_data
        except Exception as e:
            print(f"Quiz generation error: {e}")
            # Fallback quiz
            state['agent_outputs']['current_quiz'] = {
                "question": f"What is the main purpose of {state['current_topic']}?",
                "type": "open_ended"
            }
        
        # Add mock materials for now
        # state['materials_found'] = [
        #     {
        #         "title": f"Introduction to {state['current_topic']}",
        #         "content": f"A beginner's guide to understanding {state['current_topic']}",
        #         "url": "https://example.com/tutorial"
        #     },
        #     {
        #         "title": f"Advanced {state['current_topic']} Concepts",
        #         "content": f"Deep dive into {state['current_topic']} for experienced developers",
        #         "url": "https://example.com/advanced"
        #     }
        # ]
        
        # state['current_understanding_level'] = 5.0
        research_agent = ResearchAgent()
        state = await research_agent.find_materials(state)
        
        return state