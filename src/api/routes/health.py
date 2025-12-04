"""
Health check and status routes
"""
from fastapi import APIRouter
from typing import Optional
from ...core.ollama import OllamaClient
from ...core.rag import RAGSystem

health_router = APIRouter(prefix="/api", tags=["health"])

# Global instances (will be initialized by app)
ollama_client: Optional[OllamaClient] = None
rag_system: Optional[RAGSystem] = None
vector_store_loaded: bool = False


def init_health_routes(client: OllamaClient, rag: RAGSystem, rag_loaded: bool):
    """Initialize health routes with dependencies"""
    global ollama_client, rag_system, vector_store_loaded
    ollama_client = client
    rag_system = rag
    vector_store_loaded = rag_loaded


@health_router.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_connected = ollama_client.check_connection() if ollama_client else False
    return {
        "status": "ok",
        "ollama_connected": ollama_connected,
        "vector_store_loaded": vector_store_loaded
    }


@health_router.get("/status")
async def get_status():
    """Get server status"""
    if not ollama_client:
        return {
            "ollama_connected": False,
            "model_name": "Not configured",
            "available_models": [],
            "rag_enabled": vector_store_loaded,
            "chunks_count": 0
        }
    
    ollama_connected = ollama_client.check_connection()
    available_models = []
    
    if ollama_connected:
        available_models = ollama_client.get_available_models()
    
    return {
        "ollama_connected": ollama_connected,
        "model_name": ollama_client.model,
        "available_models": available_models,
        "rag_enabled": vector_store_loaded,
        "chunks_count": len(rag_system.chunks) if rag_system and rag_system.chunks else 0
    }
