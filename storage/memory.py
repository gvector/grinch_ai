from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json

from storage.schemas import Excuse, Evidence, NewsArticle


class InMemoryStorage:
    """Simple storage using Python dictionaries"""
    
    def __init__(self):
        self.excuses: Dict[str, Excuse] = {}
        self.evidence: Dict[str, List[Evidence]] = {}
        self.news_cache: Dict[str, NewsArticle] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
    
    def save_excuse(self, excuse: Excuse) -> str:
        """Save an excuse and return its ID"""
        self.excuses[excuse.id] = excuse
        self.cache_timestamps[f"excuse_{excuse.id}"] = datetime.now()
        return excuse.id
    
    def get_excuse(self, excuse_id: str) -> Optional[Excuse]:
        """Retrieve an excuse by ID"""
        return self.excuses.get(excuse_id)
    
    def save_evidence(self, evidence: Evidence) -> None:
        """Save evidence for an excuse"""
        if evidence.excuse_id not in self.evidence:
            self.evidence[evidence.excuse_id] = []
        self.evidence[evidence.excuse_id].append(evidence)
    
    def get_evidence(self, excuse_id: str) -> List[Evidence]:
        """Get all evidence for an excuse"""
        return self.evidence.get(excuse_id, [])
    
    def cache_news(self, key: str, articles: List[NewsArticle], ttl_hours: int = 1) -> None:
        """Cache news articles with TTL"""
        self.news_cache[key] = articles
        self.cache_timestamps[f"news_{key}"] = datetime.now()
    
    def get_cached_news(self, key: str, ttl_hours: int = 1) -> Optional[List[NewsArticle]]:
        """Get cached news if not expired"""
        cache_key = f"news_{key}"
        if cache_key not in self.cache_timestamps:
            return None
        
        timestamp = self.cache_timestamps[cache_key]
        if datetime.now() - timestamp > timedelta(hours=ttl_hours):
            # Cache expired
            del self.cache_timestamps[cache_key]
            del self.news_cache[key]
            return None
        
        return self.news_cache.get(key)
    
    def get_all_excuses(self) -> List[Excuse]:
        """Get all stored excuses"""
        return list(self.excuses.values())
    
    def search_excuses(self, situation: str) -> List[Excuse]:
        """Simple text search for similar excuses"""
        situation_lower = situation.lower()
        return [
            excuse for excuse in self.excuses.values()
            if situation_lower in excuse.text.lower()
        ]
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.news_cache.clear()
        self.cache_timestamps.clear()
    
    def export_to_json(self, filepath: str) -> None:
        """Export all data to JSON file"""
        data = {
            "excuses": [excuse.model_dump() for excuse in self.excuses.values()],
            "evidence": {
                excuse_id: [ev.model_dump() for ev in evidences]
                for excuse_id, evidences in self.evidence.items()
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def import_from_json(self, filepath: str) -> None:
        """Import data from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for excuse_data in data.get("excuses", []):
            excuse = Excuse(**excuse_data)
            self.excuses[excuse.id] = excuse
        
        for excuse_id, evidences in data.get("evidence", {}).items():
            self.evidence[excuse_id] = [Evidence(**ev) for ev in evidences]


# Global storage instance
storage = InMemoryStorage()