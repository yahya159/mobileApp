"""
Centralized configuration settings for EMSI Chatbot
"""
import os
from pathlib import Path
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

class Settings:
    """Application settings and configuration"""
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3-coder:30b")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    # For production, set CORS_ORIGINS to specific domains, e.g., "https://example.com,https://app.example.com"
    # For development, "*" allows all origins (NOT RECOMMENDED for production)
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    @classmethod
    def get_cors_origins(cls) -> list:
        """
        Get CORS allowed origins as a list
        Returns ["*"] for development, or list of specific origins for production
        """
        if cls.CORS_ORIGINS == "*":
            return ["*"]  # Development mode - allows all origins
        # Production mode - specific origins
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(",") if origin.strip()]
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # RAG Configuration
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # File Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CONFIG_DIR: Path = PROJECT_ROOT / "config"
    VECTOR_STORE_PATH: Path = DATA_DIR / "vector_store.index"
    CHUNKS_PATH: Path = DATA_DIR / "chunks.pkl"
    PDF_PATH: Path = DATA_DIR / "Brochure_EMSI.pdf"
    
    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH: Path = CONFIG_DIR / "api_server_service_account.json"
    
    # Model Default Parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 512
    DEFAULT_TOP_K: int = 40
    DEFAULT_TOP_P: float = 0.9
    
    @classmethod
    def get_ollama_generate_endpoint(cls) -> str:
        """Get Ollama generate API endpoint"""
        return f"{cls.OLLAMA_HOST}/api/generate"
    
    @classmethod
    def get_ollama_embed_endpoint(cls) -> str:
        """Get Ollama embedding API endpoint"""
        return f"{cls.OLLAMA_HOST}/api/embeddings"
    
    @classmethod
    def get_ollama_tags_endpoint(cls) -> str:
        """Get Ollama tags API endpoint"""
        return f"{cls.OLLAMA_HOST}/api/tags"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CONFIG_DIR.mkdir(exist_ok=True)

# Initialize directories on import
Settings.ensure_directories()

