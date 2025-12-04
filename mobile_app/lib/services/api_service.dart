import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Use localhost for Windows/Web, 10.0.2.2 for Android emulator
  // Users can change this in Settings if needed
  static const String _defaultBaseUrl = 'http://localhost:5000';
  
  String? _authToken;
  Future<String?> Function()? _getTokenCallback;

  void setTokenCallback(Future<String?> Function() callback) {
    _getTokenCallback = callback;
  }

  Future<String?> _getAuthToken() async {
    if (_getTokenCallback != null) {
      return await _getTokenCallback!();
    }
    return _authToken;
  }
  
  Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('api_url') ?? _defaultBaseUrl;
  }
  
  Future<String> get baseUrl async => await getBaseUrl();

  Future<Map<String, String>> _getHeaders({bool includeAuth = true}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    return headers;
  }

  Future<Map<String, dynamic>> checkHealth() async {
    try {
      final url = await baseUrl;
      final headers = await _getHeaders(includeAuth: false);
      final response = await http.get(
        Uri.parse('$url/api/health'),
        headers: headers,
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Server returned ${response.statusCode}: ${response.body}');
      }
    } on http.ClientException {
      final url = await baseUrl;
      throw Exception('Cannot connect to server at $url. Make sure the API server is running.');
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }

  Future<Map<String, dynamic>> getStatus() async {
    try {
      final url = await baseUrl;
      final headers = await _getHeaders(includeAuth: false);
      final response = await http.get(
        Uri.parse('$url/api/status'),
        headers: headers,
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }

  Future<void> sendMessageStream(
    String message, {
    bool ragEnabled = false,
    double temperature = 0.7,
    int maxTokens = 512,
    int topK = 40,
    double topP = 0.9,
    int ragTopK = 3,
    required Function(String) onChunk,
  }) async {
    final client = http.Client();
    try {
      final url = await baseUrl;
      final headers = await _getHeaders();
      headers['Accept'] = 'text/event-stream';
      final request = http.Request('POST', Uri.parse('$url/api/chat'));
      request.headers.addAll(headers);
      request.body = json.encode({
        'message': message,
        'rag_enabled': ragEnabled,
        'temperature': temperature,
        'max_tokens': maxTokens,
        'top_k': topK,
        'top_p': topP,
        'rag_top_k': ragTopK,
        'stream': true,
      });

      var response = await client.send(request).timeout(const Duration(minutes: 5));

      if (response.statusCode == 401) {
        // Token expired or invalid, try to refresh
        final token = await _getAuthToken();
        if (token != null) {
          // Retry with new token
          headers['Authorization'] = 'Bearer $token';
          final retryRequest = http.Request('POST', Uri.parse('$url/api/chat'));
          retryRequest.headers.addAll(headers);
          retryRequest.body = json.encode({
            'message': message,
            'rag_enabled': ragEnabled,
            'temperature': temperature,
            'max_tokens': maxTokens,
            'top_k': topK,
            'top_p': topP,
            'rag_top_k': ragTopK,
            'stream': true,
          });
          response = await client.send(retryRequest).timeout(const Duration(minutes: 5));
        } else {
          throw Exception('Authentication required. Please sign in again.');
        }
      }

      if (response.statusCode != 200) {
        final body = await response.stream.bytesToString();
        throw Exception('Server returned ${response.statusCode}: $body');
      }

      // Parse Server-Sent Events (SSE) stream
      final completer = Completer<void>();
      final subscription = response.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter())
          .listen(
        (line) {
          if (line.startsWith('data: ')) {
            final dataStr = line.substring(6);
            if (dataStr.trim().isEmpty) return;
            
            try {
              final data = json.decode(dataStr);
              if (data['error'] != null) {
                completer.completeError(Exception(data['error']));
                return;
              }
              if (data['content'] != null) {
                onChunk(data['content']);
              }
              if (data['done'] == true) {
                completer.complete();
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        },
        onError: (error) => completer.completeError(error),
        onDone: () {
          if (!completer.isCompleted) {
            completer.complete();
          }
        },
        cancelOnError: false,
      );
      
      await completer.future;
      await subscription.cancel();
      
    } catch (e) {
      throw Exception('Error sending message: $e');
    } finally {
      client.close();
    }
  }

  Future<String> sendMessageSimple(
    String message, {
    bool ragEnabled = false,
    double temperature = 0.7,
    int maxTokens = 512,
  }) async {
    try {
      final url = await baseUrl;
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$url/api/chat/simple'),
        headers: headers,
        body: json.encode({
          'message': message,
          'rag_enabled': ragEnabled,
          'temperature': temperature,
          'max_tokens': maxTokens,
        }),
      ).timeout(const Duration(minutes: 5));

      if (response.statusCode == 401) {
        throw Exception('Authentication required. Please sign in again.');
      }

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['content'] ?? 'No response';
      } else {
        final error = json.decode(response.body);
        throw Exception(error['error'] ?? 'Unknown error');
      }
    } catch (e) {
      throw Exception('Error sending message: $e');
    }
  }
}

