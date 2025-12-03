@echo off
echo ========================================
echo   EMSI Chatbot - Project Launcher
echo ========================================
echo.

echo [1/3] Starting API Server...
start "API Server" cmd /k "venv\Scripts\activate && python api_server.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Streamlit Web App...
start "Streamlit App" cmd /k "venv\Scripts\activate && streamlit run app.py"
timeout /t 2 /nobreak >nul

echo [3/3] Instructions:
echo.
echo API Server: http://localhost:5000
echo Web App: http://localhost:8501
echo.
echo To run the mobile app:
echo   1. cd mobile_app
echo   2. flutter pub get
echo   3. flutter run
echo.
echo Make sure Ollama is running: ollama serve
echo.
pause

