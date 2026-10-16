@echo off
title RealOrReel - AI Image Verifier (Qwen2.5-Coder:3b)
echo ========================================================
echo       REALORREEL - LOCAL AI IMAGE VERIFIER
echo  Powered by Open-Source Forensics + Qwen2.5-Coder:3b
echo ========================================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM 2. Install dependencies
echo [1/3] Checking dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Pip install had issues, attempting to continue...
)

REM 3. Prompt user about Ollama
echo.
echo [2/3] Checking AI Brain setup...
echo Make sure your local AI brain is running in another terminal window:
echo     ollama run qwen2.5-coder:3b
echo.

REM 4. Launch backend and open browser
echo [3/3] Starting RealOrReel server at http://localhost:8000 ...
start http://localhost:8000
python backend/app.py

pause
