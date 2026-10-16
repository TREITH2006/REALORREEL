#!/usr/bin/env bash
set -e

echo "========================================================"
echo "      REALORREEL - LOCAL AI IMAGE VERIFIER"
echo " Powered by Open-Source Forensics + Qwen2.5-Coder:3b"
echo "========================================================"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.9+."
    exit 1
fi

echo "[1/3] Checking dependencies..."
python3 -m pip install -r requirements.txt --quiet

echo ""
echo "[2/3] Checking AI Brain status..."
echo "Make sure Ollama is running in another terminal:"
echo "    ollama run qwen2.5-coder:3b"
echo ""

echo "[3/3] Launching RealOrReel server at http://127.0.0.1:8000 ..."
# Open browser if possible
if command -v xdg-open &> /dev/null; then
    (sleep 1.5 && xdg-open "http://127.0.0.1:8000") &
elif command -v open &> /dev/null; then
    (sleep 1.5 && open "http://127.0.0.1:8000") &
fi

python3 backend/app.py
