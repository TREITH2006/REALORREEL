### How to run locally in VS Code terminal

#### 1. Clone & navigate
`ash
git clone https://github.com/TREITH2006/REALORREEL.git
cd REALORREEL
`

#### 2. (Optional) Start Ollama in a separate terminal
`ash
ollama pull qwen2.5-coder:3b
ollama run qwen2.5-coder:3b
`

#### 3. Create & activate virtual environment (PowerShell)
`powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
`

#### 4. Install dependencies
`ash
pip install -r requirements.txt
`

#### 5. (Optional) Run diagnostic
`ash
python test_system.py
`

#### 6. Start the app
`ash
python backend/app.py
# or
.\start.bat
`

#### 7. Open in browser
http://127.0.0.1:8000
