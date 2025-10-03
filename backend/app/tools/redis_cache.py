# backend/app/tools/redis_cache.py
import redis
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from app.config import settings

class RedisCache:
    def __init__(self):
        # Parse Redis URL
        if settings.redis_url.startswith('redis://'):
            self.client = redis.from_url(settings.redis_url)
        else:
            self.client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connection
        try:
            self.client.ping()
            print("[Redis] Connected successfully")
        except Exception as e:
            print(f"[Redis] Connection failed: {e}")
            self.client = None
    
    def set_session(self, user_id: str, state: Dict[str, Any], expire_hours: int = 24) -> bool:
        """Store user session state in Redis"""
        if not self.client:
            return False
        
        try:
            key = f"session:{user_id}"
            # Convert state to JSON
            value = json.dumps(state, default=str)
            # Set with expiration
            self.client.setex(key, timedelta(hours=expire_hours), value)
            print(f"[Redis] Saved session for user {user_id}")
            return True
        except Exception as e:
            print(f"[Redis] Error saving session: {e}")
            return False
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session state from Redis"""
        if not self.client:
            return None
        
        try:
            key = f"session:{user_id}"
            value = self.client.get(key)
            if value:
                print(f"[Redis] Retrieved session for user {user_id}")
                return json.loads(value)
            return None
        except Exception as e:
            print(f"[Redis] Error getting session: {e}")
            return None
    
    def cache_llm_response(self, prompt_hash: str, response: str, expire_minutes: int = 60) -> bool:
        """Cache LLM responses to avoid redundant API calls"""
        if not self.client:
            return False
        
        try:
            key = f"llm:{prompt_hash}"
            self.client.setex(key, timedelta(minutes=expire_minutes), response)
            return True
        except:
            return False
    
    def get_cached_llm_response(self, prompt_hash: str) -> Optional[str]:
        """Get cached LLM response"""
        if not self.client:
            return None
        
        try:
            key = f"llm:{prompt_hash}"
            return self.client.get(key)
        except:
            return None
    
    def track_user_progress(self, user_id: str, topic: str, metrics: Dict[str, Any]) -> bool:
        """Track user learning progress over time"""
        if not self.client:
            return False
        
        try:
            key = f"progress:{user_id}:{topic}"
            timestamp = datetime.now().isoformat()
            
            # Store as time series
            self.client.zadd(
                key,
                {json.dumps({**metrics, "timestamp": timestamp}): datetime.now().timestamp()}
            )
            
            # Keep only last 100 entries
            self.client.zremrangebyrank(key, 0, -101)
            return True
        except Exception as e:
            print(f"[Redis] Error tracking progress: {e}")
            return False
    
    def get_user_progress(self, user_id: str, topic: str, limit: int = 10) -> list:
        """Get user's learning progress history"""
        if not self.client:
            return []
        
        try:
            key = f"progress:{user_id}:{topic}"
            # Get latest entries
            results = self.client.zrevrange(key, 0, limit - 1)
            return [json.loads(r) for r in results]
        except:
            return []
    
    def set_learning_path(self, user_id: str, path: list) -> bool:
        """Store personalized learning path"""
        if not self.client:
            return False
        
        try:
            key = f"path:{user_id}"
            self.client.set(key, json.dumps(path))
            return True
        except:
            return False
    
    def get_learning_path(self, user_id: str) -> Optional[list]:
        """Get personalized learning path"""
        if not self.client:
            return None
        
        try:
            key = f"path:{user_id}"
            value = self.client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    def increment_metric(self, user_id: str, metric: str, amount: int = 1) -> int:
        """Increment a metric counter"""
        if not self.client:
            return 0
        
        try:
            key = f"metric:{user_id}:{metric}"
            return self.client.incrby(key, amount)
        except:
            return 0
    
    def get_metric(self, user_id: str, metric: str) -> int:
        """Get a metric value"""
        if not self.client:
            return 0
        
        try:
            key = f"metric:{user_id}:{metric}"
            value = self.client.get(key)
            return int(value) if value else 0
        except:
            return 0