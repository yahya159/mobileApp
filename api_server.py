"""
Flask REST API Server for EMSI Chatbot
Exposes chatbot functionality for mobile app consumption
"""
from flask import Flask, request, jsonify, stream_with_context, Response, g
from flask_cors import CORS
import requests
import json
import os
from rag_module import RAGSystem
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
# Enable CORS for mobile app with more permissive settings for development
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Firebase Admin SDK
firebase_initialized = False
try:
    # Try to load service account from file
    service_account_path = os.path.join(os.path.dirname(__file__), 'api_server_service_account.json')
    if os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✅ Firebase Admin SDK initialized")
    else:
        print("⚠️  Firebase service account file not found. Authentication will be disabled.")
        print(f"   Expected path: {service_account_path}")
        print("   Please download service account JSON from Firebase Console and place it as 'api_server_service_account.json'")
except Exception as e:
    print(f"⚠️  Failed to initialize Firebase Admin SDK: {e}")
    print("   Authentication will be disabled. API endpoints will be accessible without authentication.")

# Constants
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3-coder:30b"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_HOST}/api/generate"

# Global RAG system instance
rag_system = None
vector_store_loaded = False

def init_rag_system():
    """Initialize RAG system and load vector store if available"""
    global rag_system, vector_store_loaded
    if rag_system is None:
        rag_system = RAGSystem(use_ollama_embeddings=False)
        if rag_system.load_vector_store():
            vector_store_loaded = True
            print(f"✅ Vector store loaded with {len(rag_system.chunks)} chunks")
    return rag_system, vector_store_loaded

# Initialize on startup
init_rag_system()

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def verify_firebase_token(token):
    """Verify Firebase ID token and return decoded token"""
    if not firebase_initialized:
        return None
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def require_auth(f):
    """Decorator to require Firebase authentication"""
    def decorated_function(*args, **kwargs):
        if not firebase_initialized:
            # If Firebase is not initialized, allow access (for development)
            g.user = None
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            decoded_token = verify_firebase_token(token)
            
            if not decoded_token:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Store user info in Flask's g object
            g.user = {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
            }
        except Exception as e:
            return jsonify({"error": f"Authentication error: {str(e)}"}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ollama_connected = check_ollama_connection()
    return jsonify({
        "status": "ok",
        "ollama_connected": ollama_connected,
        "vector_store_loaded": vector_store_loaded
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get server status"""
    ollama_connected = check_ollama_connection()
    available_models = []
    
    if ollama_connected:
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
        except:
            pass
    
    return jsonify({
        "ollama_connected": ollama_connected,
        "model_name": MODEL_NAME,
        "available_models": available_models,
        "rag_enabled": vector_store_loaded,
        "chunks_count": len(rag_system.chunks) if rag_system and rag_system.chunks else 0
    })

@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    """Chat endpoint with streaming support"""
    data = request.json
    user_message = data.get('message', '')
    rag_enabled = data.get('rag_enabled', False)
    rag_top_k = data.get('rag_top_k', 3)
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 512)
    top_k = data.get('top_k', 40)
    top_p = data.get('top_p', 0.9)
    stream = data.get('stream', True)
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    if not check_ollama_connection():
        return jsonify({"error": "Ollama is not running. Please start it with 'ollama serve'"}), 503
    
    # Build prompt with RAG context if enabled
    prompt = user_message
    context_info = ""
    
    if rag_enabled and rag_system is not None and vector_store_loaded:
        context = rag_system.get_context_for_query(user_message, top_k=rag_top_k)
        if context:
            context_info = f"\n\n[Retrieved Context from EMSI Brochure]\n{context}\n"
            prompt = f"""Based on the following context from the EMSI brochure, please answer the user's question. If the context doesn't contain relevant information, use your general knowledge to answer.

Context:{context_info}

User Question: {user_message}

Please provide a helpful and accurate answer:"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "top_k": top_k,
            "top_p": top_p,
        }
    }
    
    if stream:
        def generate():
            try:
                response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, stream=True, timeout=300)
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'Status {response.status_code}: {response.text}'})}\n\n"
                    return
                
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield f"data: {json.dumps({'content': data['response'], 'done': data.get('done', False)})}\n\n"
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            except requests.exceptions.Timeout:
                yield f"data: {json.dumps({'error': 'Request timeout. The model may need more time to process.'})}\n\n"
            except requests.exceptions.ConnectionError:
                yield f"data: {json.dumps({'error': 'Cannot connect to Ollama. Make sure ollama serve is running.'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    else:
        # Non-streaming response
        try:
            response = requests.post(OLLAMA_GENERATE_ENDPOINT, json=payload, timeout=300)
            
            if response.status_code != 200:
                return jsonify({"error": f"Status {response.status_code}: {response.text}"}), 500
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            return jsonify({"content": full_response if full_response else "No response generated"})
        except requests.exceptions.Timeout:
            return jsonify({"error": "Request timeout"}), 504
        except requests.exceptions.ConnectionError:
            return jsonify({"error": "Cannot connect to Ollama"}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/chat/simple', methods=['POST'])
@require_auth
def chat_simple():
    """Simple non-streaming chat endpoint"""
    data = request.json
    user_message = data.get('message', '')
    rag_enabled = data.get('rag_enabled', False)
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    # Use default parameters for simple endpoint
    data['stream'] = False
    data['temperature'] = data.get('temperature', 0.7)
    data['max_tokens'] = data.get('max_tokens', 512)
    data['top_k'] = data.get('top_k', 40)
    data['top_p'] = data.get('top_p', 0.9)
    data['rag_top_k'] = data.get('rag_top_k', 3)
    
    # Reuse chat endpoint logic but force non-streaming
    return chat()

if __name__ == '__main__':
    print("🚀 Starting EMSI Chatbot API Server...")
    print(f"📡 API will be available at http://localhost:5000")
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"🔗 Ollama: {OLLAMA_HOST}")
    app.run(host='0.0.0.0', port=5000, debug=True)

