from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM Configuration
    groq_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    default_llm: str = "groq"  # groq, together, or replicate
    
    # Vector DB
    qdrant_url: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "education_materials"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Database
    database_url: str = "sqlite:///./education.db"
    
    class Config:
        env_file = ".env"

settings = Settings()