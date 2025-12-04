"""
Ollama API Client
Handles all interactions with Ollama API
"""
import requests
import json
from typing import List, Optional, Dict, Any, Iterator
from ...config import Settings


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama client
        
        Args:
            host: Ollama host URL (defaults to Settings.OLLAMA_HOST)
            model: Model name (defaults to Settings.OLLAMA_MODEL)
        """
        self.host = host or Settings.OLLAMA_HOST
        self.model = model or Settings.OLLAMA_MODEL
    
    def check_connection(self, timeout: int = 5) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(Settings.get_ollama_tags_endpoint(), timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(Settings.get_ollama_tags_endpoint(), timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except:
            pass
        return []
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_k: int = 40,
        top_p: float = 0.9,
        stream: bool = True,
        timeout: int = 300
    ) -> Iterator[Dict[str, Any]]:
        """
        Generate response from Ollama
        
        Args:
            prompt: Input prompt
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            top_k: Top K parameter
            top_p: Top P parameter
            stream: Whether to stream the response
            timeout: Request timeout in seconds
            
        Yields:
            Dictionary with response chunks
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_k": top_k,
                "top_p": top_p,
            }
        }
        
        response = requests.post(
            Settings.get_ollama_generate_endpoint(),
            json=payload,
            stream=stream,
            timeout=timeout
        )
        
        if response.status_code != 200:
            yield {"error": f"Status {response.status_code}: {response.text}"}
            return
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield data
                    if data.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
    
    def generate_complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_k: int = 40,
        top_p: float = 0.9,
        timeout: int = 300
    ) -> str:
        """
        Generate complete response (non-streaming)
        
        Args:
            prompt: Input prompt
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            top_k: Top K parameter
            top_p: Top P parameter
            timeout: Request timeout in seconds
            
        Returns:
            Complete response string
        """
        full_response = ""
        for chunk in self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_k=top_k,
            top_p=top_p,
            stream=True,
            timeout=timeout
        ):
            if "error" in chunk:
                return f"Error: {chunk['error']}"
            if "response" in chunk:
                full_response += chunk["response"]
        
        return full_response if full_response else "No response generated"
    
    def get_embedding(self, text: str, model: Optional[str] = None, timeout: int = 30) -> List[float]:
        """
        Get embedding from Ollama
        
        Args:
            text: Text to embed
            model: Embedding model name (defaults to Settings.OLLAMA_EMBEDDING_MODEL)
            timeout: Request timeout in seconds
            
        Returns:
            Embedding vector
        """
        model = model or Settings.OLLAMA_EMBEDDING_MODEL
        payload = {
            "model": model,
            "prompt": text
        }
        
        response = requests.post(
            Settings.get_ollama_embed_endpoint(),
            json=payload,
            timeout=timeout
        )
        
        if response.status_code == 200:
            return response.json().get("embedding", [])
        else:
            raise Exception(f"Ollama embedding API returned status {response.status_code}")

