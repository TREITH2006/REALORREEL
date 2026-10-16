### How to run locally (VS Code terminal)

1. Clone and navigate
   `ash
   git clone https://github.com/TREITH2006/REALORREEL.git
   cd REALORREEL
   `

2. (Optional) Start Ollama for enhanced reasoning
   `ash
   ollama pull qwen2.5-coder:3b
   ollama run qwen2.5-coder:3b
   `
   Keep this running in a separate terminal.

3. Set up Python environment
   `ash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # or: .\venv\Scripts\activate.bat  # Windows CMD
   pip install -r requirements.txt
   `

4. (Optional) Run diagnostic
   `ash
   python test_system.py
   `

5. Start the app
   `ash
   .\start.bat  # Windows
   # or: python backend/app.py
   `

6. Open http://127.0.0.1:8000 in your browser

Notes: Works fully offline. If Ollama not running, system falls back to built-in rule engine automatically.
