from typing import Dict, Any
from app.tools.llm_client import LLMClient
from app.tools.vector_store import VectorStore
import datetime
class TutorAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    # async def explain_concept(self, state: Dict[str, Any]) -> Dict[str, Any]:
    #     """Explain concept based on student's level and previous failures"""
        
    #     # Search for relevant materials
    #     relevant_materials = await self.vector_store.search(
    #         state['current_topic'],
    #         limit=3
    #     )
        
    #     context = "\n".join([m['text'] for m in relevant_materials])
        
    #     prompt = f"""
    #     You are an expert tutor. Explain {state['current_topic']} to a student.
        
    #     Student's current understanding: {state['current_understanding_level']}/10
    #     Recent mistakes: {state.get('quiz_results', [])}
        
    #     Reference materials:
    #     {context}
        
    #     Provide a clear, adaptive explanation. If the student has failed before,
    #     try a different approach (visual, analogy, step-by-step).
    #     """
        
    #     explanation = await self.llm.generate(
    #         prompt,
    #         system_prompt="You are a patient, adaptive tutor who adjusts teaching style based on student needs."
    #     )
        
    #     state['agent_outputs']['tutor_explanation'] = explanation
        
    #     # Store the explanation for future reference
    #     await self.vector_store.add_document(
    #         explanation,
    #         {
    #             "type": "explanation",
    #             "topic": state['current_topic'],
    #             "level": state['current_understanding_level']
    #         }
    #     )
        
    #     return state
    async def explain_concept(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive explanations based on student level and context"""
        
        print(f"[Tutor Agent] Starting explanation for {state['current_topic']}")
        
        # Determine explanation style based on level
        level = state['current_understanding_level']
        if level < 3:
            style = "beginner-friendly with simple analogies and no jargon"
            depth = "basic concepts only"
        elif level < 7:
            style = "clear and practical with examples"
            depth = "core concepts with some details"
        else:
            style = "technical and comprehensive"
            depth = "advanced concepts with nuances"
        
        # Track what aspects have been explained
        if 'explained_aspects' not in state:
            state['explained_aspects'] = []
        
        # Different aspects to cover over time
        aspects = [
            "fundamental concepts",
            "practical applications",
            "common use cases",
            "best practices",
            "common pitfalls",
            "advanced techniques"
        ]
        
        # Pick unexplained aspect
        unexplained = [a for a in aspects if a not in state['explained_aspects']]
        if not unexplained:
            state['explained_aspects'] = []
            unexplained = aspects
        
        import random
        current_aspect = random.choice(unexplained)
        state['explained_aspects'].append(current_aspect)
        
        # Check quiz performance for targeted explanation
        recent_mistakes = []
        if state.get('quiz_results'):
            for result in state['quiz_results'][-3:]:
                if not result.get('correct'):
                    recent_mistakes.append(result.get('feedback', ''))
        
        # Generate focused explanation
        prompt = f"""
        You are an expert tutor teaching {state['current_topic']} to a student.
        
        Student level: {level}/10 ({style})
        Learning goal: {state.get('learning_goal', 'General understanding')}
        Aspect to explain: {current_aspect}
        Depth: {depth}
        
        {"Recent mistakes to address: " + str(recent_mistakes) if recent_mistakes else ""}
        
        Create an engaging explanation that:
        1. Focuses on {current_aspect} of {state['current_topic']}
        2. Uses {style} language
        3. Is approximately 150-200 words
        4. Includes at least one concrete example
        5. {"Addresses the recent mistakes" if recent_mistakes else "Builds on basics"}
        
        Make it conversational and encouraging. Start directly with the content, no preamble.
        """
        
        # Generate with higher temperature for variety
        explanation = await self.llm.generate(
            prompt,
            system_prompt="You are an encouraging tutor who adapts explanations to student level. Be concise but clear.",
            temperature=0.8,
            max_tokens=500
        )
        
        # Validate explanation quality
        if not explanation or len(explanation.strip()) < 100:
            # Fallback with more specific content
            explanation = self._generate_fallback_explanation(state, current_aspect)
        
        # Add structure to explanation if missing
        if state['current_topic'].lower() not in explanation.lower():
            explanation = f"Let's explore {current_aspect} of {state['current_topic']}.\n\n{explanation}"
        
        state['agent_outputs']['tutor_explanation'] = explanation
        state['agent_outputs']['explanation_aspect'] = current_aspect
        
        # Update conversation history
        if 'conversation_history' not in state:
            state['conversation_history'] = []
        state['conversation_history'].append({
            "role": "tutor",
            "content": explanation,
            "aspect": current_aspect,
            "timestamp": str(datetime.now())
        })
        
        print(f"[Tutor Agent] Generated explanation for {current_aspect}")
        return state

    def _generate_fallback_explanation(self, state: Dict[str, Any], aspect: str) -> str:
        """Generate topic-specific fallback explanations"""
        
        topic = state['current_topic'].lower()
        
        fallback_templates = {
            "sql": {
                "fundamental concepts": "SQL is a language for managing databases. Think of a database as a highly organized filing cabinet, and SQL as the set of commands you use to find, add, update, or remove files. The core operations are SELECT (find data), INSERT (add data), UPDATE (modify data), and DELETE (remove data).",
                "practical applications": "SQL is used everywhere data is stored - from your bank tracking transactions to social media storing posts. For example, when you search for a product online, SQL queries find matching items from millions of records in milliseconds.",
                "common use cases": "Common SQL tasks include generating reports, finding specific customer records, calculating sales totals, and joining data from multiple tables. For instance, combining customer info with their orders to see purchase history.",
            },
            "machine learning": {
                "fundamental concepts": "Machine Learning is teaching computers to learn patterns from data instead of explicitly programming rules. Imagine teaching a child to recognize cats - instead of describing every possible cat, you show many examples until they learn the pattern.",
                "practical applications": "ML powers recommendation systems (Netflix suggestions), image recognition (face unlock), and predictions (weather forecasting). When Spotify creates your weekly playlist, it's using ML to analyze your listening patterns.",
                "common use cases": "ML excels at classification (spam detection), regression (price prediction), clustering (customer segmentation), and pattern recognition (fraud detection).",
            },
            "python": {
                "fundamental concepts": "Python is a programming language designed to be readable and simple. It uses indentation to organize code, making it visually clear. Variables store data, functions perform tasks, and libraries provide pre-built tools.",
                "practical applications": "Python is used for web development (Instagram), data science (analyzing COVID data), automation (scheduling tasks), and AI (ChatGPT). Its simplicity makes it perfect for beginners and experts alike.",
                "common use cases": "Common Python tasks include automating repetitive work, analyzing spreadsheet data, building websites, creating games, and developing AI models. Many companies use Python scripts to save hours of manual work.",
            }
        }
        
        # Get topic-specific content or generic
        topic_content = fallback_templates.get(topic, {})
        if aspect in topic_content:
            return topic_content[aspect]
        
        # Generic fallback
        return f"Let's explore {aspect} of {state['current_topic']}. This topic builds on what you've learned and introduces new concepts that will deepen your understanding. Each element we discuss connects to form a complete picture of how {state['current_topic']} works in practice."