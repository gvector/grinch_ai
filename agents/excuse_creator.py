from storage.schemas import (
    ExcuseRequest, 
    Excuse, 
    NewsArticle,
    NewsCategory
)
from utils.helpers import generate_excuse_id
from utils.llm_client import llm_client
from config import settings

from datetime import datetime
from typing import List, Optional
import json


EXCUSE_CREATOR_PROMPT = """You are a creative excuse generator. Your job is to create believable, clever excuses for various situations.

Given:
- A situation that needs an excuse
- Optional context about the situation
- Optional news articles to base the excuse on

Create {num_excuses} different excuse options. Each excuse should:
1. Be believable and plausible
2. Fit the situation naturally
3. If news articles are provided, creatively connect to them
4. Be appropriate for the tone and recipient
5. Include a risk assessment (low/medium/high)

Return ONLY a valid JSON object with this structure:
{{
    "excuses": [
        {{
            "text": "The excuse text",
            "plausibility_score": 0.85,
            "creativity_score": 0.75,
            "risk_level": "low",
            "explanation": "Why this excuse works"
        }}
    ]
}}

Important rules:
- plausibility_score: 0.0-1.0 (higher = more believable)
- creativity_score: 0.0-1.0 (higher = more creative/unique)
- risk_level: "low", "medium", or "high"
- If absurd/funny news is used, balance creativity with plausibility
"""


class ExcuseCreatorAgent:
    """
    Agent that generates creative excuses
    Simple implementation without DataPizza for now
    """
    
    def __init__(self):
        self.name = "Excuse Creator"
        self.llm = llm_client
    
    def generate_excuses(
        self,
        request: ExcuseRequest,
        news_articles: Optional[List[NewsArticle]] = None
    ) -> List[Excuse]:
        """
        Generate excuses for a given situation
        
        Args:
            request: The excuse request with situation and context
            news_articles: Optional news to base excuses on
            
        Returns:
            List of generated Excuse objects
        """
        print(f"[{self.name}] Generating excuses for: {request.situation}")
        
        # Build the prompt with all context
        user_message = self._build_user_message(request, news_articles)
        
        messages = [
            {
                "role": "system",
                "content": EXCUSE_CREATOR_PROMPT.format(
                    num_excuses=settings.max_excuses_per_request
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        # Get response from LLM
        try:
            print(f"[{self.name}] Calling LLM...")
            response = self.llm.chat(
                messages=messages,
                temperature=0.8,  # Higher creativity
                response_format="json"
            )
            
            print(f"[{self.name}] Received response, parsing...")
            
            # Parse response
            data = self.llm.parse_json_response(response)
            excuses = self._parse_excuses(data, request, news_articles)
            
            print(f"[{self.name}] Successfully generated {len(excuses)} excuses")
            return excuses
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            print(f"[{self.name}] Creating fallback excuse...")
            return self._create_fallback_excuse(request)
    
    def _build_user_message(
        self,
        request: ExcuseRequest,
        news_articles: Optional[List[NewsArticle]]
    ) -> str:
        """Build the user message with all context"""
        msg = f"Situation: {request.situation}\n"
        
        if request.context:
            msg += f"Context: {request.context}\n"
        
        if request.recipient:
            msg += f"Recipient: {request.recipient}\n"
        
        msg += f"Tone: {request.tone.value}\n"
        
        if request.preferred_news_category:
            msg += f"Preferred news type: {request.preferred_news_category.value}\n"
        
        if news_articles:
            msg += f"\n--- Available News Articles ({len(news_articles)}) ---\n"
            for i, article in enumerate(news_articles[:5], 1):  # Max 5 articles
                msg += f"\n{i}. [{article.category.value}] {article.title}\n"
                msg += f"   {article.summary}\n"
                msg += f"   Absurdity: {article.absurdity_score:.2f}\n"
        
        return msg
    
    def _parse_excuses(
        self,
        data: dict,
        request: ExcuseRequest,
        news_articles: Optional[List[NewsArticle]]
    ) -> List[Excuse]:
        """Parse LLM response into Excuse objects"""
        excuses = []
        
        excuse_list = data.get("excuses", [])
        if not excuse_list:
            print(f"[{self.name}] Warning: No excuses in response, using fallback")
            return self._create_fallback_excuse(request)
        
        for excuse_data in excuse_list:
            # Get the most relevant news article if available
            news_ref = news_articles[0] if news_articles else None
            
            try:
                excuse = Excuse(
                    id=generate_excuse_id(),
                    text=excuse_data.get("text", ""),
                    news_reference=news_ref,
                    plausibility_score=float(excuse_data.get("plausibility_score", 0.5)),
                    creativity_score=float(excuse_data.get("creativity_score", 0.5)),
                    risk_level=excuse_data.get("risk_level", "medium"),
                    explanation=excuse_data.get("explanation", ""),
                    created_at=datetime.now()
                )
                excuses.append(excuse)
            except Exception as e:
                print(f"[{self.name}] Error parsing excuse: {e}")
                continue
        
        if not excuses:
            return self._create_fallback_excuse(request)
        
        return excuses
    
    def _create_fallback_excuse(self, request: ExcuseRequest) -> List[Excuse]:
        """Create a simple fallback excuse if LLM fails"""
        return [
            Excuse(
                id=generate_excuse_id(),
                text=f"Mi scuso per l'inconveniente riguardo: {request.situation}",
                news_reference=None,
                plausibility_score=0.7,
                creativity_score=0.3,
                risk_level="low",
                explanation="Scusa generica di fallback",
                created_at=datetime.now()
            )
        ]