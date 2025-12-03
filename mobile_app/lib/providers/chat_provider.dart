import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/message.dart';
import 'auth_provider.dart';

class ChatProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  AuthProvider? _authProvider;

  void setAuthProvider(AuthProvider authProvider) {
    _authProvider = authProvider;
    _apiService.setTokenCallback((_) async {
      return await _authProvider?.getIdToken();
    });
  }
  final List<Message> _messages = [];
  bool _isLoading = false;
  bool _isConnected = false;
  String? _error;

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isConnected => _isConnected;
  String? get error => _error;

  ChatProvider() {
    checkConnection();
  }

  Future<void> checkConnection() async {
    try {
      final status = await _apiService.checkHealth();
      _isConnected = status['ollama_connected'] == true;
      _error = null;
      notifyListeners();
    } catch (e) {
      _isConnected = false;
      _error = 'Cannot connect to server';
      notifyListeners();
    }
  }

  Future<void> sendMessage(String text, {
    bool ragEnabled = false,
    double temperature = 0.7,
    int maxTokens = 512,
    Function(String)? onChunk,
  }) async {
    if (text.trim().isEmpty) return;

    // Add user message
    final userMessage = Message(
      text: text,
      isUser: true,
      timestamp: DateTime.now(),
    );
    _messages.add(userMessage);
    notifyListeners();

    // Add placeholder for assistant response
    final assistantMessageIndex = _messages.length;
    _messages.add(Message(
      text: '',
      isUser: false,
      timestamp: DateTime.now(),
    ));
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      String fullResponse = '';
      
      await _apiService.sendMessageStream(
        text,
        ragEnabled: ragEnabled,
        temperature: temperature,
        maxTokens: maxTokens,
        onChunk: (chunk) {
          fullResponse += chunk;
          // Update the message by replacing it in the list
          _messages[assistantMessageIndex] = Message(
            text: fullResponse,
            isUser: false,
            timestamp: _messages[assistantMessageIndex].timestamp,
          );
          if (onChunk != null) {
            onChunk(fullResponse);
          }
          notifyListeners();
        },
      );

      // Final update
      _messages[assistantMessageIndex] = Message(
        text: fullResponse,
        isUser: false,
        timestamp: _messages[assistantMessageIndex].timestamp,
      );
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      _messages[assistantMessageIndex] = Message(
        text: 'Error: ${e.toString()}',
        isUser: false,
        timestamp: _messages[assistantMessageIndex].timestamp,
      );
      notifyListeners();
    }
  }

  void clearMessages() {
    _messages.clear();
    _error = null;
    notifyListeners();
  }

  Future<Map<String, dynamic>> getStatus() async {
    try {
      return await _apiService.getStatus();
    } catch (e) {
      return {'error': e.toString()};
    }
  }
}

