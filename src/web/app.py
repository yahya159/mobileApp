"""
Streamlit Web Application for EMSI Chatbot
"""
import streamlit as st
import os
from pathlib import Path

from ..config import Settings
from ..core.ollama import OllamaClient
from ..core.rag import RAGSystem


# Configure Streamlit
st.set_page_config(
    page_title="EMSI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stChatMessage {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ollama_client" not in st.session_state:
    st.session_state.ollama_client = OllamaClient()
if "rag_system" not in st.session_state:
    st.session_state.rag_system = RAGSystem(use_ollama_embeddings=False)
    if st.session_state.rag_system.load_vector_store():
        st.session_state.vector_store_loaded = True
    else:
        st.session_state.vector_store_loaded = False
if "rag_enabled" not in st.session_state:
    st.session_state.rag_enabled = False


def generate_response(
    user_message: str,
    temperature: float,
    max_tokens: int,
    top_k: int,
    top_p: float,
    message_placeholder=None,
    rag_enabled: bool = False,
    rag_top_k: int = 3
):
    """Generate response from Ollama with optional RAG"""
    try:
        # Build prompt with RAG context if enabled
        prompt = user_message
        
        if rag_enabled and st.session_state.vector_store_loaded:
            context = st.session_state.rag_system.get_context_for_query(user_message, top_k=rag_top_k)
            if context:
                prompt = f"""Based on the following context from the EMSI brochure, please answer the user's question. If the context doesn't contain relevant information, use your general knowledge to answer.

Context:
{context}

User Question: {user_message}

Please provide a helpful and accurate answer:"""
        
        # Generate response with streaming
        full_response = ""
        for chunk in st.session_state.ollama_client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_k=top_k,
            top_p=top_p,
            stream=True,
            timeout=300
        ):
            if "error" in chunk:
                return f"Error: {chunk['error']}"
            if "response" in chunk:
                full_response += chunk["response"]
                # Update UI in real-time if placeholder is provided
                if message_placeholder is not None:
                    message_placeholder.markdown(full_response + "▌")
        
        return full_response if full_response else "No response generated"
    
    except Exception as e:
        return f"Error: {str(e)}"


def clear_chat_history():
    """Clear chat history"""
    st.session_state.messages = []
    st.success("Chat history cleared!")


# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    st.divider()
    
    # Connection Status
    ollama_client = st.session_state.ollama_client
    if ollama_client.check_connection():
        st.success("✅ Ollama Connected")
        available_models = ollama_client.get_available_models()
        if available_models:
            st.info(f"📦 Available Models:\n" + "\n".join(f"• {m}" for m in available_models[:5]))
    else:
        st.error("❌ Ollama Not Connected\nMake sure to run 'ollama serve' in terminal")
    
    st.divider()
    
    # RAG Configuration
    st.subheader("📚 RAG (Document Retrieval)")
    
    # RAG Enable/Disable
    rag_enabled = st.checkbox(
        "Enable RAG",
        value=st.session_state.rag_enabled,
        help="Enable Retrieval-Augmented Generation using the EMSI brochure"
    )
    st.session_state.rag_enabled = rag_enabled
    
    # Vector Store Status
    if st.session_state.vector_store_loaded:
        st.success("✅ Document Indexed")
        if st.session_state.rag_system and st.session_state.rag_system.chunks:
            st.caption(f"📄 {len(st.session_state.rag_system.chunks)} chunks loaded")
    else:
        st.warning("⚠️ No document indexed")
        # Check if PDF exists but not indexed
        if Settings.PDF_PATH.exists():
            st.info("📄 PDF detected! Scroll down to index it.")
    
    # Document Upload/Index Section
    st.divider()
    st.subheader("📄 Document Management")
    
    # Indexing parameters (shown when not indexed)
    use_ollama_emb = False
    chunk_size = Settings.RAG_CHUNK_SIZE
    chunk_overlap = Settings.RAG_CHUNK_OVERLAP
    
    if not st.session_state.vector_store_loaded:
        use_ollama_emb = st.checkbox(
            "Use Ollama for embeddings",
            value=False,
            help="Requires Ollama embedding model (e.g., nomic-embed-text)"
        )
        chunk_size = st.slider(
            "Chunk Size",
            500,
            2000,
            Settings.RAG_CHUNK_SIZE,
            100,
            help="Size of text chunks in characters"
        )
        chunk_overlap = st.slider(
            "Chunk Overlap",
            100,
            500,
            Settings.RAG_CHUNK_OVERLAP,
            50,
            help="Overlap between chunks in characters"
        )
    
    # File uploader for PDF
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=['pdf'],
        help="Upload the EMSI brochure PDF to enable RAG"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        Settings.ensure_directories()
        with open(Settings.PDF_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ PDF uploaded! Click 'Index Document' to process it.")
    
    # Index button for uploaded or existing PDF
    pdf_exists = Settings.PDF_PATH.exists()
    
    if pdf_exists and not st.session_state.vector_store_loaded:
        st.info("📄 **Brochure_EMSI.pdf** found! Ready to index.")
    
    if (uploaded_file is not None or pdf_exists) and not st.session_state.vector_store_loaded:
        st.markdown("---")
        st.markdown("### 🚀 Start Indexing")
        st.caption("Click the button below to process and index the PDF document. This may take a few minutes depending on the document size.")
        
        if st.button("🔍 Index Document", use_container_width=True, type="primary"):
            pdf_to_index = str(Settings.PDF_PATH)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(status, progress):
                status_text.text(status)
                progress_bar.progress(progress)
            
            try:
                # Initialize RAG system
                st.session_state.rag_system = RAGSystem(use_ollama_embeddings=use_ollama_emb)
                
                # Build vector store with progress callback
                st.session_state.rag_system.build_vector_store(
                    pdf_to_index,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    progress_callback=update_progress
                )
                
                status_text.text("Saving vector store...")
                progress_bar.progress(0.95)
                
                # Save vector store
                st.session_state.rag_system.save_vector_store()
                st.session_state.vector_store_loaded = True
                
                progress_bar.progress(1.0)
                status_text.text("✅ Complete!")
                
                st.success("✅ Document indexed successfully!")
                st.balloons()
                st.rerun()
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error indexing document: {str(e)}")
                st.exception(e)
                st.info("💡 **Tips:**\n- Make sure all dependencies are installed: `pip install -r requirements.txt`\n- Check that the PDF file is not corrupted\n- Try reducing chunk size if memory issues occur\n- If using Ollama embeddings, ensure the embedding model is installed: `ollama pull nomic-embed-text`")
    
    # RAG Parameters
    if rag_enabled and st.session_state.vector_store_loaded:
        st.divider()
        st.subheader("🔍 RAG Parameters")
        rag_top_k = st.slider(
            "Retrieval Count (Top K)",
            min_value=1,
            max_value=10,
            value=Settings.RAG_TOP_K,
            step=1,
            help="Number of document chunks to retrieve for context"
        )
    else:
        rag_top_k = Settings.RAG_TOP_K
    
    st.divider()
    st.subheader("📊 Model Parameters")
    
    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=Settings.DEFAULT_TEMPERATURE,
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )
    
    # Max Tokens
    max_tokens = st.slider(
        "Max Tokens",
        min_value=1,
        max_value=4096,
        value=Settings.DEFAULT_MAX_TOKENS,
        step=50,
        help="Maximum length of generated response"
    )
    
    # Top K
    top_k = st.slider(
        "Top K",
        min_value=0,
        max_value=100,
        value=Settings.DEFAULT_TOP_K,
        step=1,
        help="Consider only top K most likely tokens (0 = disabled)"
    )
    
    # Top P
    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=Settings.DEFAULT_TOP_P,
        step=0.05,
        help="Cumulative probability threshold"
    )
    
    st.divider()
    
    # Display current settings
    st.subheader("📋 Current Settings")
    st.caption(f"**Model:** {Settings.OLLAMA_MODEL}")
    st.caption(f"**Temperature:** {temperature}")
    st.caption(f"**Max Tokens:** {max_tokens}")
    st.caption(f"**Top K:** {top_k}")
    st.caption(f"**Top P:** {top_p}")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_chat_history()
    
    st.divider()
    st.caption("Made with ❤️ using Streamlit & Ollama")

# Main Chat Interface
st.title("🤖 EMSI Chatbot")
rag_status = " | RAG: 🟢 Enabled" if (st.session_state.rag_enabled and st.session_state.vector_store_loaded) else " | RAG: ⚪ Disabled"
st.caption(f"Powered by {Settings.OLLAMA_MODEL} | Status: {'🟢 Online' if ollama_client.check_connection() else '🔴 Offline'}{rag_status}")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    if not ollama_client.check_connection():
        st.error("❌ Ollama is not running. Please start it with 'ollama serve' in terminal.")
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            spinner_text = "Retrieving context and thinking..." if (st.session_state.rag_enabled and st.session_state.vector_store_loaded) else "Thinking..."
            with st.spinner(spinner_text):
                response = generate_response(
                    prompt,
                    temperature,
                    max_tokens,
                    top_k,
                    top_p,
                    message_placeholder,
                    rag_enabled=st.session_state.rag_enabled,
                    rag_top_k=rag_top_k if (st.session_state.rag_enabled and st.session_state.vector_store_loaded) else Settings.RAG_TOP_K
                )
            message_placeholder.markdown(response)
        
        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": response})

