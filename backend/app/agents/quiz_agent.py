from typing import Dict, Any, List
import json
from app.tools.llm_client import LLMClient

class QuizAgent:
    def __init__(self):
        self.llm = LLMClient()
    
    async def generate_quiz(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive quiz based on understanding level"""
        
        difficulty_map = {
            (0, 3): "basic",
            (4, 6): "intermediate", 
            (7, 10): "advanced"
        }
        
        level = state['current_understanding_level']
        difficulty = next(v for k, v in difficulty_map.items() if k[0] <= level <= k[1])
        
        prompt = f"""
        Create a quiz question about {state['current_topic']}.
        Difficulty: {difficulty}
        
        Consider previous wrong answers to avoid similar mistakes:
        {state.get('quiz_results', [])}
        
        Return as JSON:
        {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "..."
        }}
        """
        
        quiz_json = await self.llm.generate(prompt, temperature=0.5)
        
        try:
            quiz_data = json.loads(quiz_json)
        except:
            # Fallback quiz structure
            quiz_data = {
                "question": f"Explain the main concept of {state['current_topic']}",
                "type": "open_ended"
            }
        
        state['agent_outputs']['current_quiz'] = quiz_data
        return state
    
    # async def evaluate_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
    #     """Evaluate student's answer"""
        
    #     quiz = state['agent_outputs'].get('current_quiz', {})
        
    #     if quiz.get('type') == 'open_ended':
    #         prompt = f"""
    #         Question: {quiz['question']}
    #         Student Answer: {answer}
            
    #         Evaluate the answer. Return JSON:
    #         {{
    #             "correct": true/false,
    #             "score": 0-10,
    #             "feedback": "...",
    #             "misconceptions": ["list", "of", "misconceptions"]
    #         }}
    #         """
    #     else:
    #         correct = answer == quiz.get('correct_answer')
    #         result = {
    #             "correct": correct,
    #             "score": 10 if correct else 0,
    #             "feedback": quiz.get('explanation', ''),
    #             "misconceptions": []
    #         }
            
    #         state['quiz_results'].append(result)
            
    #         # Update understanding level
    #         if correct:
    #             state['current_understanding_level'] = min(10, 
    #                 state['current_understanding_level'] + 0.5)
    #         else:
    #             state['current_understanding_level'] = max(0,
    #                 state['current_understanding_level'] - 0.25)
            
    #         return state
        
    #     evaluation = await self.llm.generate(prompt)
    #     try:
    #         result = json.loads(evaluation)
    #         state['quiz_results'].append(result)
            
    #         # Update understanding based on score
    #         state['current_understanding_level'] = (
    #             state['current_understanding_level'] * 0.7 + 
    #             result['score'] * 0.3
    #         )
    #     except:
    #         pass
        
    #     return state
    # async def evaluate_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
    #     """Evaluate student's answer and generate new quiz"""
        
    #     quiz = state['agent_outputs'].get('current_quiz', {})
        
    #     # Check if answer is correct
    #     if quiz.get('correct_answer'):
    #         correct = answer == quiz.get('correct_answer')
    #         result = {
    #             "correct": correct,
    #             "score": 10 if correct else 0,
    #             "feedback": quiz.get('explanation', 'Keep trying!'),
    #             "misconceptions": []
    #         }
    #     else:
    #         # For open-ended questions
    #         result = {
    #             "correct": True,
    #             "score": 7,
    #             "feedback": "Good effort! Let's continue.",
    #             "misconceptions": []
    #         }
        
    #     # Add to quiz results
    #     if 'quiz_results' not in state:
    #         state['quiz_results'] = []
    #     state['quiz_results'].append(result)
        
    #     # Update understanding level
    #     if result['correct']:
    #         state['current_understanding_level'] = min(10, 
    #             state['current_understanding_level'] + 0.5)
    #     else:
    #         state['current_understanding_level'] = max(0,
    #             state['current_understanding_level'] - 0.25)
        
    #     # Generate a NEW quiz question
    #     difficulty = "harder" if result['correct'] else "easier"
        
    #     new_quiz_prompt = f"""
    #     The student just answered a question about {state['current_topic']}.
    #     They got it {"correct" if result['correct'] else "wrong"}.
        
    #     Create a {difficulty} multiple choice question about {state['current_topic']}.
        
    #     Return ONLY valid JSON:
    #     {{
    #         "question": "A different question than before",
    #         "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    #         "correct_answer": "A",
    #         "explanation": "Why this answer is correct"
    #     }}
    #     """
        
    #     try:
    #         quiz_response = await self.llm.generate(new_quiz_prompt, temperature=0.7)
            
    #         # Clean the response
    #         if "```json" in quiz_response:
    #             quiz_response = quiz_response.split("```json")[1].split("```")[0]
    #         elif "```" in quiz_response:
    #             quiz_response = quiz_response.split("```")[1]
            
    #         import json
    #         new_quiz = json.loads(quiz_response.strip())
    #         state['agent_outputs']['current_quiz'] = new_quiz
            
    #     except Exception as e:
    #         print(f"Error generating new quiz: {e}")
    #         # Generate a simple fallback quiz
    #         state['agent_outputs']['current_quiz'] = {
    #             "question": f"Can you explain another aspect of {state['current_topic']}?",
    #             "type": "open_ended"
    #         }
        
    #     return state
    # async def evaluate_answer(self, state: Dict[str, Any], answer: str) -> Dict[str, Any]:
    #     """Evaluate student's answer and generate new quiz"""
        
    #     quiz = state['agent_outputs'].get('current_quiz', {})
        
    #     # DEBUG: Print what we're comparing
    #     print(f"=== QUIZ EVALUATION DEBUG ===")
    #     print(f"Quiz question: {quiz.get('question', 'No question')}")
    #     print(f"Quiz options: {quiz.get('options', [])}")
    #     print(f"Correct answer: {quiz.get('correct_answer')}")
    #     print(f"User submitted: {answer}")
        
    #     # Check if answer is correct
    #     correct = False
    #     if quiz.get('options'):  # Multiple choice question
    #         correct_answer = quiz.get('correct_answer', '').strip()
            
    #         # The problem: answer might be "A) Option text" but correct_answer is just "A"
    #         # Or vice versa
            
    #         # If user sent full option text (e.g., "A) First option")
    #         if answer.startswith(('A)', 'B)', 'C)', 'D)')):
    #             # Extract just the letter
    #             user_letter = answer[0]
    #             # Compare with correct answer
    #             if correct_answer.startswith(('A)', 'B)', 'C)', 'D)')):
    #                 correct = answer == correct_answer
    #             else:
    #                 correct = user_letter == correct_answer
    #         # If user sent just the option text without letter
    #         else:
    #             # Check if this matches any option
    #             options = quiz.get('options', [])
    #             for i, opt in enumerate(options):
    #                 if opt == answer or opt.endswith(answer):
    #                     # Found which option was selected
    #                     user_letter = chr(65 + i)  # Convert 0->A, 1->B, etc
    #                     if len(correct_answer) == 1:
    #                         correct = user_letter == correct_answer
    #                     break
            
    #         print(f"Is correct: {correct}")
            
    #         result = {
    #             "correct": correct,
    #             "score": 10 if correct else 0,
    #             "feedback": quiz.get('explanation', 'Keep trying!') if not correct else "Great job! You got it right!",
    #             "misconceptions": []
    #         }
    #     else:
    #         # Open-ended question
    #         result = {
    #             "correct": True,
    #             "score": 7,
    #             "feedback": "Good effort! Let's continue.",
    #             "misconceptions": []
    #         }
        
    #     # Add to quiz results
    #     if 'quiz_results' not in state:
    #         state['quiz_results'] = []
    #     state['quiz_results'].append(result)
        
    #     # Update understanding level
    #     old_level = state['current_understanding_level']
    #     if result['correct']:
    #         state['current_understanding_level'] = min(10, old_level + 1.0)
    #         print(f"Correct! Level: {old_level} -> {state['current_understanding_level']}")
    #     else:
    #         state['current_understanding_level'] = max(0, old_level - 0.5)
    #         print(f"Wrong! Level: {old_level} -> {state['current_understanding_level']}")
        
    #     # Generate a NEW quiz question
    #     difficulty = "harder" if result['correct'] else "easier"
        
    #     new_quiz_prompt = f"""
    #     Create a {difficulty} multiple choice question about {state['current_topic']}.
        
    #     IMPORTANT: For correct_answer, use ONLY the letter (A, B, C, or D).
        
    #     Return ONLY this exact JSON format:
    #     {{
    #         "question": "New question here",
    #         "options": ["First option", "Second option", "Third option", "Fourth option"],
    #         "correct_answer": "B",
    #         "explanation": "Why B is correct"
    #     }}
    #     """
        
    #     try:
    #         quiz_response = await self.llm.generate(new_quiz_prompt, temperature=0.7)
    #         print(f"Raw LLM response: {quiz_response[:200]}...")  # First 200 chars
            
    #         # Extract JSON from response
    #         import json
    #         import re
            
    #         # Try to find JSON in the response
    #         json_match = re.search(r'\{[^}]+\}', quiz_response, re.DOTALL)
    #         if json_match:
    #             quiz_text = json_match.group()
    #         else:
    #             quiz_text = quiz_response
            
    #         # Clean up common issues
    #         quiz_text = quiz_text.replace('```json', '').replace('```', '').strip()
            
    #         new_quiz = json.loads(quiz_text)
    #         state['agent_outputs']['current_quiz'] = new_quiz
    #         print(f"New quiz generated successfully")
            
    #     except Exception as e:
    #         print(f"Error generating new quiz: {e}")
    #         # Fallback quiz
    #         state['agent_outputs']['current_quiz'] = {
    #             "question": f"What else would you like to know about {state['current_topic']}?",
    #             "type": "open_ended"
    #         }
        
    #     print(f"=== END DEBUG ===\n")
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
        
        # Generate new quiz
        difficulty = "harder" if is_correct else "easier"
        prompt = f"""
        Create a {difficulty} multiple choice question about {state['current_topic']}.
        
        Format EXACTLY like this JSON:
        {{
            "question": "Your question here",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": "B",
            "explanation": "Why B is correct"
        }}
        
        IMPORTANT: correct_answer must be just the letter: A, B, C, or D
        """
        
        try:
            response = await self.llm.generate(prompt, temperature=0.5)
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                new_quiz = json.loads(json_match.group())
                state['agent_outputs']['current_quiz'] = new_quiz
        except Exception as e:
            print(f"Error generating new quiz: {e}")
        
        return state