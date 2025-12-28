from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExcuseTone(str, Enum):
    """Tone options for excuse communication"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    APOLOGETIC = "apologetic"
    CONFIDENT = "confident"


class NewsCategory(str, Enum):
    """News categories for excuse generation"""
    NATIONAL_FUNNY = "national_funny"          # Notizie nazionali divertenti
    NATIONAL_ABSURD = "national_absurd"        # Notizie nazionali assurde
    INTERNATIONAL_FUNNY = "international_funny"  # Notizie internazionali divertenti
    INTERNATIONAL_ABSURD = "international_absurd"  # Notizie internazionali assurde


class ExcuseRequest(BaseModel):
    """User's request for an excuse"""
    situation: str = Field(..., description="The situation requiring an excuse")
    context: Optional[str] = Field(None, description="Additional context about the situation")
    recipient: Optional[str] = Field(None, description="Who will receive the excuse")
    tone: ExcuseTone = Field(ExcuseTone.PROFESSIONAL, description="Desired tone")
    preferred_news_category: Optional[NewsCategory] = Field(None, description="Preferred type of news to base excuse on")
    
    class Config:
        json_schema_extra = {
            "example": {
                "situation": "late to meeting",
                "context": "work meeting at 9am",
                "recipient": "manager",
                "tone": "professional",
                "preferred_news_category": "national_absurd"
            }
        }


class NewsCategory(str, Enum):
    """News categories for excuse generation"""
    NATIONAL_FUNNY = "national_funny"          # Notizie nazionali divertenti
    NATIONAL_ABSURD = "national_absurd"        # Notizie nazionali assurde
    INTERNATIONAL_FUNNY = "international_funny"  # Notizie internazionali divertenti
    INTERNATIONAL_ABSURD = "international_absurd"  # Notizie internazionali assurde


class NewsArticle(BaseModel):
    """Scraped news article data"""
    title: str
    summary: str
    url: Optional[str] = None
    source: str
    published_at: datetime
    category: NewsCategory = Field(..., description="News category type")
    relevance_score: float = Field(0.0, ge=0.0, le=1.0, description="How relevant to the excuse")
    absurdity_score: float = Field(0.0, ge=0.0, le=1.0, description="How absurd/unusual the news is")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Uomo blocca traffico per salvare paperella",
                "summary": "Un automobilista ha fermato il traffico per 20 minuti...",
                "url": "https://news.example.com/paperella",
                "source": "La Repubblica",
                "published_at": "2024-01-15T08:00:00Z",
                "category": "national_funny",
                "relevance_score": 0.85,
                "absurdity_score": 0.9
            }
        }


class Excuse(BaseModel):
    """Generated excuse with metadata"""
    id: str = Field(..., description="Unique identifier")
    text: str = Field(..., description="The excuse itself")
    news_reference: Optional[NewsArticle] = Field(None, description="Supporting news article")
    plausibility_score: float = Field(..., ge=0.0, le=1.0, description="How believable (0-1)")
    creativity_score: float = Field(..., ge=0.0, le=1.0, description="How creative (0-1)")
    risk_level: str = Field(..., description="low, medium, high - risk of getting caught")
    explanation: str = Field(..., description="Why this excuse works")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "exc_123",
                "text": "I was caught in the traffic jam caused by the downtown road closure",
                "plausibility_score": 0.9,
                "creativity_score": 0.6,
                "risk_level": "low",
                "explanation": "Based on real news event, easily verifiable"
            }
        }


class Evidence(BaseModel):
    """Supporting evidence for an excuse"""
    excuse_id: str
    evidence_type: str = Field(..., description="screenshot, image, link, document")
    content: str = Field(..., description="Evidence content or URL")
    description: str = Field(..., description="What this evidence shows")
    credibility_score: float = Field(..., ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "excuse_id": "exc_123",
                "evidence_type": "link",
                "content": "https://news.example.com/traffic",
                "description": "News article about road closure",
                "credibility_score": 0.95
            }
        }


class DraftedMessage(BaseModel):
    """AI-drafted message ready to send"""
    excuse_id: str
    recipient_type: str = Field(..., description="manager, friend, family, etc.")
    tone: ExcuseTone
    subject: Optional[str] = Field(None, description="Email subject if applicable")
    body: str = Field(..., description="The message body")
    alternative_versions: List[str] = Field(default_factory=list, description="Other variations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "excuse_id": "exc_123",
                "recipient_type": "manager",
                "tone": "professional",
                "subject": "Running Late Due to Traffic",
                "body": "Good morning, I wanted to let you know..."
            }
        }


class ExcuseGenerationResult(BaseModel):
    """Complete result from the excuse generation process"""
    request: ExcuseRequest
    excuses: List[Excuse]
    selected_excuse: Optional[Excuse] = None
    evidence: Optional[List[Evidence]] = None
    drafted_message: Optional[DraftedMessage] = None
    generation_time_seconds: float