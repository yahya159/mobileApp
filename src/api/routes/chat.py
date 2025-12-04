"""
Chat routes
"""
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ...core.ollama import OllamaClient
from ...core.rag import RAGSystem
from ...config import Settings
from ..middleware.auth import get_current_user

chat_router = APIRouter(prefix="/api", tags=["chat"])

# Global instances (will be initialized by app)
ollama_client: Optional[OllamaClient] = None
rag_system: Optional[RAGSystem] = None
vector_store_loaded: bool = False


def init_chat_routes(client: OllamaClient, rag: RAGSystem, rag_loaded: bool):
    """Initialize chat routes with dependencies"""
    global ollama_client, rag_system, vector_store_loaded
    ollama_client = client
    rag_system = rag
    vector_store_loaded = rag_loaded


def build_prompt_with_rag(user_message: str, rag_enabled: bool, rag_top_k: int) -> str:
    """Build prompt with RAG context if enabled"""
    prompt = user_message
    
    if rag_enabled and rag_system is not None and vector_store_loaded:
        context = rag_system.get_context_for_query(user_message, top_k=rag_top_k)
        if context:
            prompt = f"""Based on the following context from the EMSI brochure, please answer the user's question. If the context doesn't contain relevant information, use your general knowledge to answer.

Context:
{context}

User Question: {user_message}

Please provide a helpful and accurate answer:"""
    
    return prompt


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    rag_enabled: bool = False
    rag_top_k: int = Settings.RAG_TOP_K
    temperature: float = Settings.DEFAULT_TEMPERATURE
    max_tokens: int = Settings.DEFAULT_MAX_TOKENS
    top_k: int = Settings.DEFAULT_TOP_K
    top_p: float = Settings.DEFAULT_TOP_P
    stream: bool = True


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str


@chat_router.post("/chat")
async def chat(
    request: ChatRequest,
    user: Optional[dict] = Depends(get_current_user)
):
    """Chat endpoint with streaming support"""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    if not ollama_client or not ollama_client.check_connection():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Please start it with 'ollama serve'"
        )
    
    # Build prompt with RAG context if enabled
    prompt = build_prompt_with_rag(request.message, request.rag_enabled, request.rag_top_k)
    
    if request.stream:
        async def generate():
            try:
                for chunk in ollama_client.generate(
                    prompt=prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_k=request.top_k,
                    top_p=request.top_p,
                    stream=True,
                    timeout=300
                ):
                    if "error" in chunk:
                        yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                        return
                    if "response" in chunk:
                        yield f"data: {json.dumps({'content': chunk['response'], 'done': chunk.get('done', False)})}\n\n"
                    if chunk.get('done', False):
                        break
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Non-streaming response
        try:
            response = ollama_client.generate_complete(
                prompt=prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_k=request.top_k,
                top_p=request.top_p,
                timeout=300
            )
            return ChatResponse(content=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/simple", response_model=ChatResponse)
async def chat_simple(
    request: ChatRequest,
    user: Optional[dict] = Depends(get_current_user)
):
    """Simple non-streaming chat endpoint"""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Force non-streaming
    request.stream = False
    
    # Use default parameters if not provided
    if request.temperature is None:
        request.temperature = Settings.DEFAULT_TEMPERATURE
    if request.max_tokens is None:
        request.max_tokens = Settings.DEFAULT_MAX_TOKENS
    if request.top_k is None:
        request.top_k = Settings.DEFAULT_TOP_K
    if request.top_p is None:
        request.top_p = Settings.DEFAULT_TOP_P
    if request.rag_top_k is None:
        request.rag_top_k = Settings.RAG_TOP_K
    
    # Build prompt with RAG context if enabled
    prompt = build_prompt_with_rag(request.message, request.rag_enabled, request.rag_top_k)
    
    try:
        response = ollama_client.generate_complete(
            prompt=prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_k=request.top_k,
            top_p=request.top_p,
            timeout=300
        )
        return ChatResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
