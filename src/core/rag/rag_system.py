"""
RAG (Retrieval-Augmented Generation) System
Handles PDF processing, text chunking, embeddings, and vector search
"""
import pickle
from typing import List, Tuple, Optional, Callable
from pathlib import Path
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss

from ...config import Settings
from ..ollama import OllamaClient


class RAGSystem:
    """RAG System for document retrieval and context generation"""
    
    def __init__(self, use_ollama_embeddings: bool = False, embedding_model: Optional[str] = None):
        """
        Initialize RAG System
        
        Args:
            use_ollama_embeddings: If True, use Ollama's embedding API. If False, use sentence-transformers
            embedding_model: Model name for Ollama embeddings (e.g., "nomic-embed-text")
        """
        self.use_ollama_embeddings = use_ollama_embeddings
        self.embedding_model_name = embedding_model or Settings.OLLAMA_EMBEDDING_MODEL
        self.embedding_model = None
        self.vector_store = None
        self.chunks: List[str] = []
        self.dimension: Optional[int] = None
        self.ollama_client = OllamaClient() if use_ollama_embeddings else None
        
        # Load sentence-transformers model if not using Ollama
        if not use_ollama_embeddings:
            try:
                self.embedding_model = SentenceTransformer(Settings.RAG_EMBEDDING_MODEL)
                self.dimension = self.embedding_model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Warning: Could not load sentence-transformers model: {e}")
                print("Falling back to Ollama embeddings...")
                self.use_ollama_embeddings = True
                self.ollama_client = OllamaClient()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text"""
        if self.use_ollama_embeddings:
            if not self.ollama_client:
                self.ollama_client = OllamaClient()
            embedding = self.ollama_client.get_embedding(text, model=self.embedding_model_name)
            if self.dimension is None:
                self.dimension = len(embedding)
            return np.array(embedding, dtype=np.float32)
        else:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            if self.dimension is None:
                self.dimension = embedding.shape[0]
            return embedding.astype(np.float32)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        chunk_size = chunk_size or Settings.RAG_CHUNK_SIZE
        chunk_overlap = chunk_overlap or Settings.RAG_CHUNK_OVERLAP
        
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [chunk for chunk in chunks if chunk]  # Remove empty chunks
    
    def build_vector_store(
        self,
        pdf_path: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Build vector store from PDF
        
        Args:
            pdf_path: Path to PDF file
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            progress_callback: Optional callback function(status, progress) for progress updates
        """
        chunk_size = chunk_size or Settings.RAG_CHUNK_SIZE
        chunk_overlap = chunk_overlap or Settings.RAG_CHUNK_OVERLAP
        
        if progress_callback:
            progress_callback("Extracting text from PDF...", 0.1)
        else:
            print("Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if progress_callback:
            progress_callback("Chunking text...", 0.2)
        else:
            print("Chunking text...")
        self.chunks = self.chunk_text(text, chunk_size, chunk_overlap)
        
        if not self.chunks:
            raise Exception("No text chunks were created from the PDF")
        
        if progress_callback:
            progress_callback(f"Creating embeddings for {len(self.chunks)} chunks...", 0.3)
        else:
            print(f"Creating embeddings for {len(self.chunks)} chunks...")
        embeddings = []
        
        for i, chunk in enumerate(self.chunks):
            progress = 0.3 + (i / len(self.chunks)) * 0.6
            if progress_callback and (i + 1) % 10 == 0:
                progress_callback(f"Processing chunk {i + 1}/{len(self.chunks)}...", progress)
            elif not progress_callback and (i + 1) % 10 == 0:
                print(f"Processing chunk {i + 1}/{len(self.chunks)}...")
            embedding = self.get_embedding(chunk)
            embeddings.append(embedding)
        
        # Convert to numpy array
        if progress_callback:
            progress_callback("Building vector index...", 0.9)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        self.dimension = embeddings_array.shape[1]
        self.vector_store = faiss.IndexFlatL2(self.dimension)
        self.vector_store.add(embeddings_array)
        
        if progress_callback:
            progress_callback(f"✅ Vector store created with {len(self.chunks)} chunks!", 1.0)
        else:
            print(f"Vector store created with {len(self.chunks)} chunks and dimension {self.dimension}")
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of tuples (chunk_text, distance)
        """
        top_k = top_k or Settings.RAG_TOP_K
        
        if self.vector_store is None or len(self.chunks) == 0:
            return []
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        distances, indices = self.vector_store.search(query_embedding, min(top_k, len(self.chunks)))
        
        # Return results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        return results
    
    def save_vector_store(self):
        """Save vector store and chunks to disk"""
        if self.vector_store is None:
            return
        
        Settings.ensure_directories()
        
        # Save FAISS index
        faiss.write_index(self.vector_store, str(Settings.VECTOR_STORE_PATH))
        # Save chunks
        with open(Settings.CHUNKS_PATH, 'wb') as f:
            pickle.dump(self.chunks, f)
        print(f"Vector store saved to {Settings.VECTOR_STORE_PATH}")
        print(f"Chunks saved to {Settings.CHUNKS_PATH}")
    
    def load_vector_store(self) -> bool:
        """Load vector store and chunks from disk"""
        if not Settings.VECTOR_STORE_PATH.exists() or not Settings.CHUNKS_PATH.exists():
            return False
        
        try:
            # Load FAISS index
            self.vector_store = faiss.read_index(str(Settings.VECTOR_STORE_PATH))
            # Load chunks
            with open(Settings.CHUNKS_PATH, 'rb') as f:
                self.chunks = pickle.load(f)
            
            # Get dimension from index
            self.dimension = self.vector_store.d
            
            print(f"Vector store loaded with {len(self.chunks)} chunks")
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def get_context_for_query(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Formatted context string
        """
        top_k = top_k or Settings.RAG_TOP_K
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, (chunk, distance) in enumerate(results, 1):
            context_parts.append(f"[Context {i}]\n{chunk}\n")
        
        return "\n".join(context_parts)

