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
├── app.py                 # Streamlit web application
├── api_server.py          # Flask REST API server (for mobile app)
├── rag_module.py          # RAG system implementation
├── requirements.txt       # Python dependencies
├── mobile_app/           # Flutter mobile application
│   ├── lib/              # Flutter source code
│   ├── android/          # Android configuration
│   └── pubspec.yaml      # Flutter dependencies
└── Brochure_EMSI.pdf     # Document for RAG (if available)
```

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

### 2. Start Ollama

```bash
ollama serve
```

Keep this running in a separate terminal.

### 3. Run the Web Application

```bash
streamlit run app.py
```

The web app will open at `http://localhost:8501`

### 4. Run the API Server (for Mobile App)

```bash
python api_server.py
```

The API server will run at `http://localhost:5000`

### 5. Run the Mobile App

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

The Flask API server provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/status` - Server status and configuration
- `POST /api/chat` - Chat endpoint with streaming support
- `POST /api/chat/simple` - Simple non-streaming chat endpoint

### Example API Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is EMSI?",
    "rag_enabled": true,
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

## Configuration

### Model Configuration

Edit `app.py` or `api_server.py` to change the model:

```python
MODEL_NAME = "qwen3-coder:30b"  # Change to your preferred model
```

### RAG Configuration

- **Chunk Size**: Default 1000 characters
- **Chunk Overlap**: Default 200 characters
- **Top K Retrieval**: Number of document chunks to retrieve (default: 3)

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
- Check that vector store files exist (`vector_store.index`, `chunks.pkl`)
- Re-index the document if needed

## Development

### Adding New Features

1. **Web App**: Modify `app.py` for Streamlit features
2. **API**: Modify `api_server.py` for new endpoints
3. **RAG**: Modify `rag_module.py` for RAG improvements
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

