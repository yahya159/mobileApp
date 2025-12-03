import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../providers/chat_provider.dart';
import '../providers/auth_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: Consumer<SettingsProvider>(
        builder: (context, settingsProvider, _) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Connection Status
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Connection Status',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Consumer<ChatProvider>(
                        builder: (context, chatProvider, _) {
                          return Row(
                            children: [
                              Icon(
                                chatProvider.isConnected
                                    ? Icons.check_circle
                                    : Icons.error,
                                color: chatProvider.isConnected
                                    ? Colors.green
                                    : Colors.red,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                chatProvider.isConnected
                                    ? 'Connected to Server'
                                    : 'Not Connected',
                                style: TextStyle(
                                  color: chatProvider.isConnected
                                      ? Colors.green
                                      : Colors.red,
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () {
                          Provider.of<ChatProvider>(context, listen: false)
                              .checkConnection();
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text('Refresh Connection'),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // API URL
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'API Server URL',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        decoration: const InputDecoration(
                          labelText: 'Server URL',
                          hintText: 'http://10.0.2.2:5000',
                          border: OutlineInputBorder(),
                        ),
                        controller: TextEditingController(
                          text: settingsProvider.apiUrl,
                        ),
                        onChanged: (value) {
                          settingsProvider.setApiUrl(value);
                        },
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Note: Use 10.0.2.2 for Android emulator, or your computer\'s IP for physical device',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // RAG Settings
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'RAG (Document Retrieval)',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      SwitchListTile(
                        title: const Text('Enable RAG'),
                        subtitle: const Text(
                          'Use document context for better answers',
                        ),
                        value: settingsProvider.ragEnabled,
                        onChanged: (value) {
                          settingsProvider.setRagEnabled(value);
                        },
                      ),
                      if (settingsProvider.ragEnabled) ...[
                        const SizedBox(height: 8),
                        Text('Retrieval Count (Top K): ${settingsProvider.ragTopK}'),
                        Slider(
                          value: settingsProvider.ragTopK.toDouble(),
                          min: 1,
                          max: 10,
                          divisions: 9,
                          label: settingsProvider.ragTopK.toString(),
                          onChanged: (value) {
                            settingsProvider.setRagTopK(value.toInt());
                          },
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Model Parameters
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Model Parameters',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text('Temperature: ${settingsProvider.temperature.toStringAsFixed(1)}'),
                      Slider(
                        value: settingsProvider.temperature,
                        min: 0.0,
                        max: 2.0,
                        divisions: 20,
                        label: settingsProvider.temperature.toStringAsFixed(1),
                        onChanged: (value) {
                          settingsProvider.setTemperature(value);
                        },
                      ),
                      const SizedBox(height: 16),
                      Text('Max Tokens: ${settingsProvider.maxTokens}'),
                      Slider(
                        value: settingsProvider.maxTokens.toDouble(),
                        min: 100,
                        max: 2048,
                        divisions: 19,
                        label: settingsProvider.maxTokens.toString(),
                        onChanged: (value) {
                          settingsProvider.setMaxTokens(value.toInt());
                        },
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // User Info & Logout
              Consumer<AuthProvider>(
                builder: (context, authProvider, _) {
                  if (authProvider.user != null) {
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Account',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            if (authProvider.user!.displayName != null)
                              Text('Name: ${authProvider.user!.displayName}'),
                            if (authProvider.user!.email != null)
                              Text('Email: ${authProvider.user!.email}'),
                            const SizedBox(height: 16),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton.icon(
                                onPressed: () async {
                                  await authProvider.signOut();
                                  if (context.mounted) {
                                    Navigator.of(context).popUntil((route) => route.isFirst);
                                  }
                                },
                                icon: const Icon(Icons.logout),
                                label: const Text('Sign Out'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red,
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }
                  return const SizedBox.shrink();
                },
              ),

              const SizedBox(height: 16),

              // Server Info
              Consumer<ChatProvider>(
                builder: (context, chatProvider, _) {
                  return FutureBuilder<Map<String, dynamic>>(
                    future: chatProvider.getStatus(),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Card(
                          child: Padding(
                            padding: EdgeInsets.all(16),
                            child: Center(child: CircularProgressIndicator()),
                          ),
                        );
                      }

                      if (snapshot.hasError || !snapshot.hasData) {
                        return const SizedBox.shrink();
                      }

                      final status = snapshot.data!;
                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Server Information',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              if (status['model_name'] != null)
                                Text('Model: ${status['model_name']}'),
                              if (status['rag_enabled'] != null)
                                Text('RAG: ${status['rag_enabled'] ? "Enabled" : "Disabled"}'),
                              if (status['chunks_count'] != null)
                                Text('Document Chunks: ${status['chunks_count']}'),
                            ],
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ],
          );
        },
      ),
    );
  }
}

