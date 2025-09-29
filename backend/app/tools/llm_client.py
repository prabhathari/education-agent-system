from typing import Dict, List, Optional
from groq import Groq
import together
import httpx
from app.config import settings

class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.default_llm
        
        if self.provider == "groq" and settings.groq_api_key:
            self.client = Groq(api_key=settings.groq_api_key)
        elif self.provider == "together" and settings.together_api_key:
            together.api_key = settings.together_api_key
            self.client = together
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: int = 1000) -> str:
        
        if self.provider == "groq":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # or "llama2-70b-4096"
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        elif self.provider == "together":
            prompt_full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = together.Complete.create(
                model="meta-llama/Llama-2-70b-chat-hf",
                prompt=prompt_full,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response['choices'][0]['text']