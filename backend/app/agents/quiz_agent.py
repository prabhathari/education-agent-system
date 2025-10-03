from typing import Dict, Any, List
import json
from app.tools.llm_client import LLMClient
import random
import hashlib

class QuizAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    # async def generate_quiz(self, state: Dict[str, Any]) -> Dict[str, Any]:
    #     """Generate adaptive quiz based on understanding level"""
        
    #     difficulty_map = {
    #         (0, 3): "basic",
    #         (4, 6): "intermediate", 
    #         (7, 10): "advanced"
    #     }
        
    #     level = state['current_understanding_level']
    #     difficulty = next(v for k, v in difficulty_map.items() if k[0] <= level <= k[1])
        
    #     # STEP 1: Search for existing questions to avoid repetition
    #     past_questions = await self.vector_store.search(
    #         f"{state['current_topic']} quiz",
    #         limit=10
    #     )
        
    #     # Extract just the question texts
    #     questions_to_avoid = []
    #     for pq in past_questions:
    #         if pq.get('metadata', {}).get('type') == 'quiz_question':
    #             questions_to_avoid.append(pq.get('text', ''))
        
    #     # STEP 2: Include the questions to avoid in the prompt
    #     prompt = f"""
    #     Create a quiz question about {state['current_topic']}.
    #     Difficulty: {difficulty}
        
    #     DO NOT ask these questions (already asked):
    #     {questions_to_avoid}
        
    #     Consider previous wrong answers to avoid similar mistakes:
    #     {state.get('quiz_results', [])}
        
    #     Create a COMPLETELY NEW question that hasn't been asked before.
        
    #     Return as JSON:
    #     {{
    #         "question": "...",
    #         "options": ["A", "B", "C", "D"],
    #         "correct_answer": "A",
    #         "explanation": "..."
    #     }}
    #     """
        
    #     quiz_json = await self.llm.generate(prompt, temperature=0.7)  # Higher temp for variety
        
    #     try:
    #         quiz_data = json.loads(quiz_json)
            
    #         # STEP 3: Store the new question
    #         if quiz_data and 'question' in quiz_data:
    #             await self.vector_store.add_document(
    #                 quiz_data['question'],
    #                 {
    #                     "type": "quiz_question",
    #                     "topic": state['current_topic'],
    #                     "user_id": state['user_id']
    #                 }
    #             )
    #             print(f"[Quiz] Stored new question: {quiz_data['question'][:50]}...")
            
    #     except:
    #         # Fallback quiz structure
    #         quiz_data = {
    #             "question": f"Explain the main concept of {state['current_topic']}",
    #             "type": "open_ended"
    #         }
        
    #     state['agent_outputs']['current_quiz'] = quiz_data
    #     return state
    


    # async def generate_quiz(self, state: Dict[str, Any]) -> Dict[str, Any]:
    #     """Generate adaptive quiz based on understanding level"""
        
    #     difficulty_map = {
    #         (0, 3): "basic",
    #         (4, 6): "intermediate", 
    #         (7, 10): "advanced"
    #     }
        
    #     level = state['current_understanding_level']
    #     difficulty = next(v for k, v in difficulty_map.items() if k[0] <= level <= k[1])
        
    #     # Get past questions from vector store
    #     past_questions = await self.vector_store.search(
    #         f"{state['current_topic']} quiz",
    #         limit=20
    #     )
        
    #     past_question_texts = [
    #         pq.get('text', '') 
    #         for pq in past_questions 
    #         if pq.get('metadata', {}).get('type') == 'quiz_question'
    #     ]
        
    #     # Define question templates to force variety
    #     question_templates = {
    #         "basic": [
    #             f"What is the primary purpose of {{concept}} in {state['current_topic']}?",
    #             f"Which of the following best describes {{concept}}?",
    #             f"What does {{concept}} do in {state['current_topic']}?",
    #             f"When would you use {{concept}}?",
    #             f"What is the correct syntax for {{concept}}?",
    #         ],
    #         "intermediate": [
    #             f"What is the difference between {{concept1}} and {{concept2}} in {state['current_topic']}?",
    #             f"Which scenario would benefit most from using {{concept}}?",
    #             f"What happens when you combine {{concept1}} with {{concept2}}?",
    #             f"What are the advantages of using {{concept}}?",
    #             f"How does {{concept}} improve performance in {state['current_topic']}?",
    #         ],
    #         "advanced": [
    #             f"What are the performance implications of {{concept}}?",
    #             f"In which edge case would {{concept}} fail?",
    #             f"How would you optimize {{concept}} for production use?",
    #             f"What are the security considerations when using {{concept}}?",
    #             f"Compare the efficiency of {{concept1}} versus {{concept2}}",
    #         ]
    #     }
        
    #     # SQL-specific concepts to ask about
    #     sql_concepts = {
    #         "basic": ["SELECT", "INSERT", "DELETE", "UPDATE", "WHERE", "FROM", "CREATE TABLE"],
    #         "intermediate": ["JOIN", "GROUP BY", "HAVING", "ORDER BY", "DISTINCT", "BETWEEN", "IN", "EXISTS"],
    #         "advanced": ["INDEX", "TRANSACTION", "TRIGGER", "STORED PROCEDURE", "VIEW", "NORMALIZATION", "ACID"]
    #     }
        
    #     # Pick unused concepts
    #     concepts = sql_concepts.get(difficulty, sql_concepts["basic"])
    #     unused_concepts = []
        
    #     for concept in concepts:
    #         # Check if we've asked about this concept
    #         concept_asked = any(concept.lower() in q.lower() for q in past_question_texts)
    #         if not concept_asked:
    #             unused_concepts.append(concept)
        
    #     # If all concepts used, pick random one
    #     if not unused_concepts:
    #         unused_concepts = concepts
        
    #     # Generate question using template
    #     selected_concept = random.choice(unused_concepts)
    #     templates = question_templates.get(difficulty, question_templates["basic"])
    #     template = random.choice(templates)
        
    #     # Create specific question
    #     if "concept1" in template and "concept2" in template:
    #         concept2 = random.choice([c for c in concepts if c != selected_concept])
    #         question_base = template.replace("{{concept1}}", selected_concept).replace("{{concept2}}", concept2)
    #     else:
    #         question_base = template.replace("{{concept}}", selected_concept)
        
    #     # Generate quiz with specific question
    #     prompt = f"""
    #     Create a multiple choice quiz question EXACTLY about this:
    #     "{question_base}"
        
    #     Topic: {state['current_topic']}
    #     Concept to test: {selected_concept}
        
    #     Return as JSON:
    #     {{
    #         "question": "{question_base}",
    #         "options": ["option A", "option B", "option C", "option D"],
    #         "correct_answer": "A",
    #         "explanation": "Clear explanation"
    #     }}
        
    #     Make sure the question is exactly about {selected_concept}.
    #     """
        
    #     quiz_json = await self.llm.generate(prompt, temperature=0.3)
        
    #     try:
    #         quiz_data = json.loads(quiz_json)
            
    #         # Store the question
    #         if quiz_data and 'question' in quiz_data:
    #             await self.vector_store.add_document(
    #                 quiz_data['question'],
    #                 {
    #                     "type": "quiz_question",
    #                     "topic": state['current_topic'],
    #                     "user_id": state['user_id'],
    #                     "concept_tested": selected_concept,
    #                     "difficulty": difficulty
    #                 }
    #             )
    #             print(f"[Quiz] Generated question about: {selected_concept}")
            
    #     except:
    #         quiz_data = {
    #             "question": f"Explain how {selected_concept} works in {state['current_topic']}",
    #             "type": "open_ended"
    #         }
        
    #     state['agent_outputs']['current_quiz'] = quiz_data
    #     return state
    async def generate_quiz(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive quiz based on understanding level"""
        
        difficulty_map = {
            (0, 3): "basic",
            (4, 6): "intermediate", 
            (7, 10): "advanced"
        }
        
        level = state['current_understanding_level']
        difficulty = next(v for k, v in difficulty_map.items() if k[0] <= level <= k[1])
        
        # Track asked question types to ensure variety
        if 'question_types_asked' not in state:
            state['question_types_asked'] = []
        
        # Different question types for variety
        question_types = [
            "definition",
            "purpose", 
            "syntax",
            "comparison",
            "example",
            "advantage",
            "use_case",
            "best_practice",
            "common_mistake",
            "performance"
        ]
        
        # Find unused question types
        unused_types = [qt for qt in question_types if qt not in state['question_types_asked']]
        if not unused_types:
            state['question_types_asked'] = []  # Reset if all used
            unused_types = question_types
        
        # Pick a question type
        import random
        selected_type = random.choice(unused_types)
        state['question_types_asked'].append(selected_type)
        
        # Generate type-specific prompts
        type_prompts = {
            "definition": f"What is the definition of a key concept in {state['current_topic']}?",
            "purpose": f"What is the main purpose of a specific feature in {state['current_topic']}?",
            "syntax": f"What is the correct syntax for a common operation in {state['current_topic']}?",
            "comparison": f"What is the difference between two related concepts in {state['current_topic']}?",
            "example": f"Which is a valid example of using {state['current_topic']}?",
            "advantage": f"What is a key advantage of using {state['current_topic']}?",
            "use_case": f"When would you typically use a specific feature of {state['current_topic']}?",
            "best_practice": f"What is a best practice when working with {state['current_topic']}?",
            "common_mistake": f"What is a common mistake to avoid in {state['current_topic']}?",
            "performance": f"Which approach is more efficient in {state['current_topic']}?"
        }
        
        # Build prompt with explicit variety instruction
        prompt = f"""
        Create a {difficulty} level multiple choice question about {state['current_topic']}.
        
        Question type: {selected_type}
        Question focus: {type_prompts[selected_type]}
        
        IMPORTANT: 
        - This is question #{len(state.get('quiz_results', [])) + 1} for this user
        - Make it about a DIFFERENT aspect than previous questions
        - Focus specifically on the {selected_type} aspect
        
        Previous questions asked: {len(state.get('quiz_results', []))}
        
        Return as JSON:
        {{
            "question": "A unique question about {state['current_topic']}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "B",
            "explanation": "Clear explanation"
        }}
        
        The question MUST be about {selected_type} aspect of {state['current_topic']}.
        """
        
        # Add randomization seed based on question count
        question_num = len(state.get('quiz_results', [])) + 1
        temperature = 0.7 + (question_num * 0.05)  # Increase temperature for more variety
        
        quiz_json = await self.llm.generate(prompt, temperature=min(temperature, 1.0))
        
        try:
            # Clean and parse JSON
            import json
            import re
            json_match = re.search(r'\{.*?\}', quiz_json, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
            else:
                quiz_data = json.loads(quiz_json)
                
            # Add metadata
            quiz_data['question_type'] = selected_type
            quiz_data['question_number'] = question_num
            
        except Exception as e:
            print(f"[Quiz] Parse error: {e}")
            # Fallback quiz
            quiz_data = {
                "question": f"Explain a key {selected_type} aspect of {state['current_topic']}",
                "type": "open_ended"
            }
        
        state['agent_outputs']['current_quiz'] = quiz_data
        print(f"[Quiz] Generated {selected_type} question #{question_num}")
        
        return state

    # async def evaluate_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
    #     """Evaluate student's answer properly"""
        
    #     quiz = state['agent_outputs'].get('current_quiz', {})
        
    #     print(f"\n=== ANSWER EVALUATION ===")
    #     print(f"Question: {quiz.get('question')}")
    #     print(f"Options: {quiz.get('options')}")
    #     print(f"Correct answer stored: '{quiz.get('correct_answer')}'")
    #     print(f"User submitted: '{answer}'")
        
    #     # Get the correct answer (might be "B" or "Structured Query Language")
    #     correct_answer = quiz.get('correct_answer', '').strip()
    #     user_answer = answer.strip()
        
    #     # Check if correct_answer is a letter (A, B, C, D)
    #     if correct_answer in ['A', 'B', 'C', 'D']:
    #         # Need to compare with what user clicked
    #         # User might have sent the full text like "Structured Query Method"
    #         # We need to find which option that is
    #         options = quiz.get('options', [])
    #         user_letter = None
            
    #         for i, option in enumerate(options):
    #             if option == user_answer:
    #                 user_letter = chr(65 + i)  # Convert 0->A, 1->B, etc.
    #                 break
            
    #         is_correct = (user_letter == correct_answer)
    #         print(f"User clicked option {user_letter}, correct is {correct_answer}")
            
    #     else:
    #         # correct_answer might be the full text
    #         is_correct = (user_answer == correct_answer)
        
    #     print(f"Result: {'CORRECT' if is_correct else 'WRONG'}")
    #     print(f"======================\n")
        
    #     # Create result with better feedback
    #     if is_correct:
    #         feedback_text = "Correct! Well done!"
    #     else:
    #         # Show what the right answer was
    #         if correct_answer in ['A', 'B', 'C', 'D']:
    #             options = quiz.get('options', [])
    #             correct_index = ord(correct_answer) - 65  # Convert A->0, B->1, etc.
    #             if correct_index < len(options):
    #                 correct_text = options[correct_index]
    #                 feedback_text = f"The correct answer was: {correct_text}. {quiz.get('explanation', '')}"
    #             else:
    #                 feedback_text = f"The correct answer was {correct_answer}. {quiz.get('explanation', '')}"
    #         else:
    #             feedback_text = f"The correct answer was: {correct_answer}. {quiz.get('explanation', '')}"
        
    #     result = {
    #         "correct": is_correct,
    #         "score": 10 if is_correct else 0,
    #         "feedback": feedback_text,
    #         "misconceptions": []
    #     }
        
    #     # Store result
    #     if 'quiz_results' not in state:
    #         state['quiz_results'] = []
    #     state['quiz_results'].append(result)
        
    #     # Update understanding level
    #     if is_correct:
    #         state['current_understanding_level'] = min(10, 
    #             state['current_understanding_level'] + 1.0)
    #         print(f"Understanding increased to {state['current_understanding_level']}")
    #     else:
    #         state['current_understanding_level'] = max(0,
    #             state['current_understanding_level'] - 0.5)
    #         print(f"Understanding decreased to {state['current_understanding_level']}")
        
    #     # Generate new quiz
    #     difficulty = "harder" if is_correct else "easier"
    #     prompt = f"""
    #     Create a {difficulty} multiple choice question about {state['current_topic']}.
        
    #     Format EXACTLY like this JSON:
    #     {{
    #         "question": "Your question here",
    #         "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    #         "correct_answer": "B",
    #         "explanation": "Why B is correct"
    #     }}
        
    #     IMPORTANT: correct_answer must be just the letter: A, B, C, or D
    #     """
        
    #     try:
    #         response = await self.llm.generate(prompt, temperature=0.5)
            
    #         # Extract JSON
    #         import re
    #         json_match = re.search(r'\{.*?\}', response, re.DOTALL)
    #         if json_match:
    #             new_quiz = json.loads(json_match.group())
    #             state['agent_outputs']['current_quiz'] = new_quiz
    #     except Exception as e:
    #         print(f"Error generating new quiz: {e}")
        
    #     return state
    async def evaluate_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Evaluate student's answer properly"""
        
        quiz = state['agent_outputs'].get('current_quiz', {})
        
        print(f"\n=== ANSWER EVALUATION ===")
        print(f"Question: {quiz.get('question')}")
        print(f"Options: {quiz.get('options')}")
        print(f"Correct answer stored: '{quiz.get('correct_answer')}'")
        print(f"User submitted: '{answer}'")
        
        # Get the correct answer (might be "B" or "Structured Query Language")
        correct_answer = quiz.get('correct_answer', '').strip()
        user_answer = answer.strip()
        
        # Check if correct_answer is a letter (A, B, C, D)
        if correct_answer in ['A', 'B', 'C', 'D']:
            # Need to compare with what user clicked
            # User might have sent the full text like "Structured Query Method"
            # We need to find which option that is
            options = quiz.get('options', [])
            user_letter = None
            
            for i, option in enumerate(options):
                if option == user_answer:
                    user_letter = chr(65 + i)  # Convert 0->A, 1->B, etc.
                    break
            
            is_correct = (user_letter == correct_answer)
            print(f"User clicked option {user_letter}, correct is {correct_answer}")
            
        else:
            # correct_answer might be the full text
            is_correct = (user_answer == correct_answer)
        
        print(f"Result: {'CORRECT' if is_correct else 'WRONG'}")
        print(f"======================\n")
        
        # Create result with better feedback
        if is_correct:
            feedback_text = "Correct! Well done!"
        else:
            # Show what the right answer was
            if correct_answer in ['A', 'B', 'C', 'D']:
                options = quiz.get('options', [])
                correct_index = ord(correct_answer) - 65  # Convert A->0, B->1, etc.
                if correct_index < len(options):
                    correct_text = options[correct_index]
                    feedback_text = f"The correct answer was: {correct_text}. {quiz.get('explanation', '')}"
                else:
                    feedback_text = f"The correct answer was {correct_answer}. {quiz.get('explanation', '')}"
            else:
                feedback_text = f"The correct answer was: {correct_answer}. {quiz.get('explanation', '')}"
        
        result = {
            "correct": is_correct,
            "score": 10 if is_correct else 0,
            "feedback": feedback_text,
            "misconceptions": []
        }
        
        # Store result
        if 'quiz_results' not in state:
            state['quiz_results'] = []
        state['quiz_results'].append(result)
        
        # Update understanding level
        if is_correct:
            state['current_understanding_level'] = min(10, 
                state['current_understanding_level'] + 1.0)
            print(f"Understanding increased to {state['current_understanding_level']}")
        else:
            state['current_understanding_level'] = max(0,
                state['current_understanding_level'] - 0.5)
            print(f"Understanding decreased to {state['current_understanding_level']}")
        
        # Generate next quiz using the predefined bank (not LLM)
        state = await self.generate_quiz(state)
        
        return state