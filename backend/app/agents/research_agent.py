from typing import Dict, Any, List
from app.tools.llm_client import LLMClient
from app.tools.vector_store import VectorStore

class ResearchAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    async def find_materials(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate relevant learning materials"""
        
        topic = state['current_topic']
        level = state['current_understanding_level']
        
        # Determine what kind of materials to generate based on level
        if level < 3:
            material_type = "beginner"
        elif level < 7:
            material_type = "intermediate"
        else:
            material_type = "advanced"
        
        # Generate materials using LLM
        materials_prompt = f"""
        Create 3 learning resources for {material_type} level students learning about {topic}.
        
        Return ONLY a JSON array with exactly 3 resources:
        [
            {{
                "title": "Clear, descriptive title",
                "content": "Brief description of what this resource covers (2-3 sentences)",
                "url": "https://example.com/relevant-path",
                "type": "article"
            }},
            {{
                "title": "Another resource title",
                "content": "What students will learn from this",
                "url": "https://example.com/another-path",
                "type": "video"
            }},
            {{
                "title": "Third resource title",
                "content": "Description of this resource",
                "url": "https://example.com/third-path",
                "type": "tutorial"
            }}
        ]
        
        Make the URLs look realistic (use real domain names like docs.python.org, wikipedia.org, etc.)
        Types can be: article, video, tutorial, documentation, course
        """
        
        try:
            response = await self.llm.generate(materials_prompt, temperature=0.7)
            
            # Extract JSON array
            import json
            import re
            
            # Find the JSON array in response
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                materials = json.loads(json_match.group())
            else:
                # Try parsing the whole response
                materials = json.loads(response.strip())
            
            # Store materials in state
            state['materials_found'] = materials
            state['agent_outputs']['research_materials'] = materials
            
            # Also store in vector database for future reference
            for material in materials:
                await self.vector_store.add_document(
                    f"{material['title']}: {material['content']}",
                    {
                        "type": "learning_material",
                        "topic": topic,
                        "level": material_type,
                        "url": material.get('url', ''),
                        "title": material.get('title', '')
                    }
                )
            
            print(f"Generated {len(materials)} learning materials for {topic}")
            
        except Exception as e:
            print(f"Error generating materials: {e}")
            # Fallback materials
            state['materials_found'] = [
                {
                    "title": f"Getting Started with {topic}",
                    "content": f"A comprehensive introduction to {topic} covering basic concepts and practical examples.",
                    "url": "https://docs.python.org/3/tutorial/",
                    "type": "tutorial"
                },
                {
                    "title": f"{topic} Best Practices",
                    "content": f"Learn the recommended approaches and common patterns when working with {topic}.",
                    "url": "https://realpython.com/",
                    "type": "article"
                },
                {
                    "title": f"Interactive {topic} Examples",
                    "content": f"Hands-on exercises to practice {topic} concepts with immediate feedback.",
                    "url": "https://www.w3schools.com/",
                    "type": "tutorial"
                }
            ]
        
        return state