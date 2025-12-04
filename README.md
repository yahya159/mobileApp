# EMSI Chatbot

A chatbot application powered by Ollama with RAG (Retrieval-Augmented Generation) capabilities, featuring both a web interface (Streamlit) and a mobile app (Flutter).

## Features

- 🤖 **AI-Powered Chat**: Uses Ollama LLM models for natural language conversations
- 📚 **RAG Support**: Retrieval-Augmented Generation using PDF documents (EMSI brochure)
- 💬 **Web Interface**: Streamlit-based web application
- 📱 **Mobile App**: Flutter mobile application for iOS and Android
- 🔄 **Streaming Responses**: Real-time streaming of AI responses
- ⚙️ **Configurable Parameters**: Adjustable temperature, max tokens, top-k, top-p

## Project Structure

```
emsi-chatbot/
├── src/                      # Source code
│   ├── config/              # Configuration module
│   │   └── settings.py      # Centralized settings
│   ├── core/                # Core business logic
│   │   ├── ollama/         # Ollama client
│   │   └── rag/            # RAG system
│   ├── api/                 # FastAPI server
│   │   ├── routes/         # API routes
│   │   ├── middleware/     # API middleware (auth)
│   │   └── app.py          # FastAPI app factory
│   └── web/                # Streamlit web app
│       └── app.py          # Streamlit application
├── config/                  # Configuration files
│   └── api_server_service_account.json  # Firebase credentials
├── data/                    # Data files
│   ├── Brochure_EMSI.pdf   # PDF document for RAG
│   ├── vector_store.index  # FAISS vector index
│   └── chunks.pkl          # Document chunks
├── mobile_app/             # Flutter mobile application
├── api_server.py           # API server entry point
├── app.py                  # Web app entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Architecture

The project follows a clean, modular architecture:

- **Configuration**: Centralized in `src/config/settings.py` with environment variable support
- **Core Logic**: Separated into `core/ollama` (Ollama client) and `core/rag` (RAG system)
- **API Layer**: FastAPI-based REST API with route separation and middleware
- **Web Layer**: Streamlit application for user interface
- **Data Management**: All data files organized in `data/` directory
- **Configuration Files**: All config files in `config/` directory

## Prerequisites

1. **Python 3.8+**
2. **Ollama**: Install from [ollama.ai](https://ollama.ai)
3. **Model**: Pull the required model: `ollama pull qwen3-coder:30b`
4. **Flutter SDK** (for mobile app): Install from [flutter.dev](https://flutter.dev)

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Create a `.env` file in the root directory to override default settings:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3-coder:30b
API_PORT=5000
STREAMLIT_PORT=8501
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200

# Security: For production, restrict CORS to specific domains
# CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
# Default "*" allows all origins (development only - NOT for production!)
```

### 3. Start Ollama

```bash
ollama serve
```

Keep this running in a separate terminal.

### 4. Run the Web Application

```bash
streamlit run app.py
```

Or use the batch file (Windows):

```bash
run_project.bat
```

The web app will open at `http://localhost:8501`

### 5. Run the API Server (for Mobile App)

```bash
python api_server.py
```

The API server will run at `http://localhost:5000`

### 6. Run the Mobile App

See [mobile_app/README.md](mobile_app/README.md) for detailed instructions.

## Web Application Usage

1. **Start Ollama**: Run `ollama serve` in a terminal
2. **Run Streamlit App**: Run `streamlit run app.py`
3. **Index Document** (optional): Upload or use existing PDF to enable RAG
4. **Chat**: Start asking questions in the chat interface

## Mobile Application Usage

1. **Start API Server**: Run `python api_server.py`
2. **Configure API URL**: 
   - Android Emulator: Use `http://10.0.2.2:5000`
   - Physical Device: Use your computer's IP address (e.g., `http://192.168.1.100:5000`)
3. **Run Flutter App**: 
   ```bash
   cd mobile_app
   flutter pub get
   flutter run
   ```

## API Endpoints

The FastAPI server provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/status` - Server status and configuration
- `POST /api/chat` - Chat endpoint with streaming support
- `POST /api/chat/simple` - Simple non-streaming chat endpoint

### Example API Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <firebase_token>" \
  -d '{
    "message": "What is EMSI?",
    "rag_enabled": true,
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

### API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## Configuration

### Model Configuration

Edit `src/config/settings.py` or set environment variables:

```python
OLLAMA_MODEL = "qwen3-coder:30b"  # Change to your preferred model
```

### RAG Configuration

- **Chunk Size**: Default 1000 characters (configurable via `RAG_CHUNK_SIZE`)
- **Chunk Overlap**: Default 200 characters (configurable via `RAG_CHUNK_OVERLAP`)
- **Top K Retrieval**: Number of document chunks to retrieve (default: 3)

## Security

⚠️ **Important Security Information**

This project handles sensitive credentials and API keys. Please review the security guidelines:

- **[SECURITY.md](SECURITY.md)** - Comprehensive security guidelines
- **Firebase Credentials**: Never commit credential files (now in `.gitignore`)
- **CORS Configuration**: Restrict origins in production (see [SECURITY.md](SECURITY.md))

### Quick Security Checklist

- [ ] Firebase credentials are NOT committed to git
- [ ] CORS origins are restricted in production (not `"*"`)
- [ ] API keys have restrictions set in Firebase Console
- [ ] Service account keys are rotated regularly

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Pull the model if missing: `ollama pull qwen3-coder:30b`

### Mobile App Connection Issues

- **Android Emulator**: Use `10.0.2.2` instead of `localhost`
- **Physical Device**: 
  - Ensure phone and computer are on the same WiFi
  - Check firewall settings (port 5000)
  - Use your computer's actual IP address

### RAG Issues

- Ensure PDF is indexed before enabling RAG
- Check that vector store files exist in `data/` directory
- Re-index the document if needed

## Development

### Project Structure

The project is organized into clear modules:

- **`src/config/`**: Configuration management
- **`src/core/`**: Core business logic (Ollama client, RAG system)
- **`src/api/`**: FastAPI with routes and middleware
- **`src/web/`**: Streamlit web interface
- **`config/`**: Configuration files (Firebase credentials, etc.)
- **`data/`**: Data files (PDFs, vector stores, chunks)

### Adding New Features

1. **Web App**: Modify `src/web/app.py` for Streamlit features
2. **API**: Add routes in `src/api/routes/` or modify existing ones (FastAPI routers)
3. **RAG**: Modify `src/core/rag/rag_system.py` for RAG improvements
4. **Mobile**: Modify files in `mobile_app/lib/`

### Testing

```bash
# Python tests (if available)
pytest

# Flutter tests
cd mobile_app
flutter test
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
