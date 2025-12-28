from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Provider Selection
    llm_provider: Literal["openai", "ollama"] = "ollama"  # Default to Ollama for development
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"  # Your local model
    
    # Optional: News APIs (for future use)
    news_api_key: Optional[str] = None
    
    # Optional: Storage (for future use)
    qdrant_api_key: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Application Settings
    max_excuses_per_request: int = 3
    cache_ttl_hours: int = 24
    temperature: float = 0.7  # LLM temperature
    max_tokens: int = 2000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def current_model(self) -> str:
        """Get the current model name based on provider"""
        return self.ollama_model if self.llm_provider == "ollama" else self.openai_model


# Global settings instance
settings = Settings()