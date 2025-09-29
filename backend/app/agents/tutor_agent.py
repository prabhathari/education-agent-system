from typing import Dict, Any
from app.tools.llm_client import LLMClient
from app.tools.vector_store import VectorStore

class TutorAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    async def explain_concept(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Explain concept based on student's level and previous failures"""
        
        # Search for relevant materials
        relevant_materials = await self.vector_store.search(
            state['current_topic'],
            limit=3
        )
        
        context = "\n".join([m['text'] for m in relevant_materials])
        
        prompt = f"""
        You are an expert tutor. Explain {state['current_topic']} to a student.
        
        Student's current understanding: {state['current_understanding_level']}/10
        Recent mistakes: {state.get('quiz_results', [])}
        
        Reference materials:
        {context}
        
        Provide a clear, adaptive explanation. If the student has failed before,
        try a different approach (visual, analogy, step-by-step).
        """
        
        explanation = await self.llm.generate(
            prompt,
            system_prompt="You are a patient, adaptive tutor who adjusts teaching style based on student needs."
        )
        
        state['agent_outputs']['tutor_explanation'] = explanation
        
        # Store the explanation for future reference
        await self.vector_store.add_document(
            explanation,
            {
                "type": "explanation",
                "topic": state['current_topic'],
                "level": state['current_understanding_level']
            }
        )
        
        return state