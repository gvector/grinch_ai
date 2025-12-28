from typing import List, Dict, Optional
from config import settings
import json


class LLMClient:
    """Unified interface for OpenAI and Ollama"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        if self.provider == "openai":
            from openai import OpenAI
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file")
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        
        elif self.provider == "ollama":
            import ollama
            self.client = ollama.Client(host=settings.ollama_base_url)
            self.model = settings.ollama_model
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (default from settings)
            max_tokens: Max tokens to generate (default from settings)
            response_format: "json" to request JSON output
            
        Returns:
            The assistant's response as string
        """
        temp = temperature if temperature is not None else settings.temperature
        max_tok = max_tokens if max_tokens is not None else settings.max_tokens
        
        if self.provider == "openai":
            return self._chat_openai(messages, temp, max_tok, response_format)
        else:
            return self._chat_ollama(messages, temp, max_tok, response_format)
    
    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[str]
    ) -> str:
        """OpenAI API call"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add JSON mode if requested
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[str]
    ) -> str:
        """Ollama API call"""
        options = {
            "temperature": temperature,
            "num_predict": max_tokens
        }
        
        # Add format instruction for JSON if requested
        if response_format == "json":
            # Ollama doesn't have native JSON mode, so we modify the system message
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\nYou MUST respond with valid JSON only. No other text."
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": "You MUST respond with valid JSON only. No other text."
                })
            options["format"] = "json"
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options=options
        )
        
        return response['message']['content']
    
    def test_connection(self) -> bool:
        """Test if the LLM is accessible"""
        try:
            response = self.chat(
                messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
                temperature=0.1,
                max_tokens=10
            )
            return "ok" in response.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON from LLM response
        Handles cases where the model includes extra text
        """
        # Try direct parsing first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        import re
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON-like structure
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not parse JSON from response: {response[:200]}")


# Global LLM client instance
llm_client = LLMClient()