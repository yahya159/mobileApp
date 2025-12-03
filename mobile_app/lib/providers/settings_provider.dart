import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider with ChangeNotifier {
  static const String _keyApiUrl = 'api_url';
  static const String _keyRagEnabled = 'rag_enabled';
  static const String _keyTemperature = 'temperature';
  static const String _keyMaxTokens = 'max_tokens';
  static const String _keyRagTopK = 'rag_top_k';

  String _apiUrl = 'http://localhost:5000'; // Default for Windows/Web
  bool _ragEnabled = false;
  double _temperature = 0.7;
  int _maxTokens = 512;
  int _ragTopK = 3;

  String get apiUrl => _apiUrl;
  bool get ragEnabled => _ragEnabled;
  double get temperature => _temperature;
  int get maxTokens => _maxTokens;
  int get ragTopK => _ragTopK;

  SettingsProvider() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _apiUrl = prefs.getString(_keyApiUrl) ?? 'http://localhost:5000'; // Default for Windows/Web
    _ragEnabled = prefs.getBool(_keyRagEnabled) ?? false;
    _temperature = prefs.getDouble(_keyTemperature) ?? 0.7;
    _maxTokens = prefs.getInt(_keyMaxTokens) ?? 512;
    _ragTopK = prefs.getInt(_keyRagTopK) ?? 3;
    notifyListeners();
  }

  Future<void> setApiUrl(String url) async {
    _apiUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyApiUrl, url);
    notifyListeners();
  }

  Future<void> setRagEnabled(bool enabled) async {
    _ragEnabled = enabled;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyRagEnabled, enabled);
    notifyListeners();
  }

  Future<void> setTemperature(double value) async {
    _temperature = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble(_keyTemperature, value);
    notifyListeners();
  }

  Future<void> setMaxTokens(int value) async {
    _maxTokens = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyMaxTokens, value);
    notifyListeners();
  }

  Future<void> setRagTopK(int value) async {
    _ragTopK = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyRagTopK, value);
    notifyListeners();
  }
}

