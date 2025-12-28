from datetime import datetime
from typing import List
import uuid
import re


def generate_excuse_id() -> str:
    """Generate a unique excuse ID"""
    return f"exc_{uuid.uuid4().hex[:8]}"


def generate_evidence_id() -> str:
    """Generate a unique evidence ID"""
    return f"evd_{uuid.uuid4().hex[:8]}"


def sanitize_text(text: str) -> str:
    """Clean and sanitize text input"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def calculate_relevance_score(text: str, keywords: List[str]) -> float:
    """
    Calculate how relevant a text is based on keyword matching
    Returns a score between 0 and 1
    """
    if not keywords:
        return 0.0
    
    text_lower = text.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return min(matches / len(keywords), 1.0)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract key words from text (simple version)
    Returns most common non-stopword words
    """
    # Simple stopwords list
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    
    # Clean and tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter stopwords and short words
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix