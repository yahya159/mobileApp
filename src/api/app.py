"""
FastAPI REST API Server for EMSI Chatbot
Exposes chatbot functionality for mobile app consumption
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health_router, chat_router
from .routes.health import init_health_routes
from .routes.chat import init_chat_routes
from ..core.ollama import OllamaClient
from ..core.rag import RAGSystem
from ..config import Settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="EMSI Chatbot API",
        description="REST API for EMSI Chatbot with RAG support",
        version="1.0.0"
    )
    
    # Enable CORS for mobile app
    # WARNING: In production, set CORS_ORIGINS environment variable to specific domains
    # Example: CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
    # Allowing "*" in production creates a security vulnerability
    cors_origins = Settings.get_cors_origins()
    
    if cors_origins == ["*"] and not Settings.API_DEBUG:
        print("⚠️  WARNING: CORS is set to allow all origins in production mode!")
        print("   Set CORS_ORIGINS environment variable to specific domains for security.")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    # Initialize core components
    ollama_client = OllamaClient()
    rag_system = RAGSystem(use_ollama_embeddings=False)
    vector_store_loaded = rag_system.load_vector_store()
    
    if vector_store_loaded:
        print(f"✅ Vector store loaded with {len(rag_system.chunks)} chunks")
    
    # Initialize routes with dependencies
    init_health_routes(ollama_client, rag_system, vector_store_loaded)
    init_chat_routes(ollama_client, rag_system, vector_store_loaded)
    
    # Register routers
    app.include_router(health_router)
    app.include_router(chat_router)
    
    return app


def run_server():
    """Run the API server"""
    import uvicorn
    app = create_app()
    print("🚀 Starting EMSI Chatbot API Server...")
    print(f"📡 API will be available at http://localhost:{Settings.API_PORT}")
    print(f"📚 API docs available at http://localhost:{Settings.API_PORT}/docs")
    print(f"🤖 Model: {Settings.OLLAMA_MODEL}")
    print(f"🔗 Ollama: {Settings.OLLAMA_HOST}")
    uvicorn.run(
        app,
        host=Settings.API_HOST,
        port=Settings.API_PORT,
        log_level="info" if Settings.API_DEBUG else "warning"
    )


if __name__ == '__main__':
    run_server()
