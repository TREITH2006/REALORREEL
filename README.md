# RealOrReel - Image Authenticity Verification System

RealOrReel is a completely local, privacy-first image forensics system that analyzes uploaded images to determine if they are authentic camera-captured images (REAL) or AI-generated/synthetic media (REEL). It uses open-source computer vision techniques with optional local LLM reasoning, and automatically falls back to rule-based analysis when no local model is available.

## Overview

This application runs entirely offline after installation. All image processing happens locally - no images or analysis data leave your machine. It works with or without Ollama/vLLM; if no local model is running, the built-in forensic rule engine handles analysis.

## Complete Project Structure

`
realorrell/
+-- backend/                    # FastAPI backend
�   +-- __init__.py             # Package marker
�   +-- app.py                  # FastAPI app with endpoints (/api/analyze, /api/health, etc.)
�   +-- brain_client.py         # LLM client with fallback to rule engine
�   +-- config.py               # Configuration (endpoints, timeouts, thresholds)
�   +-- forensics.py            # Forensic extraction (EXIF, ELA, FFT, noise/texture)
�   +-- samples/                # Sample test images
�       +-- sample_ai.png
�       +-- sample_real.jpg
+-- frontend/                   # Web UI
�   +-- app.js                  # Frontend logic + 3D holographic renderer
�   +-- index.html              # UI
�   +-- style.css               # Styling
+-- requirements.txt            # Python dependencies
+-- start.bat                  # Windows launcher
+-- start.sh                   # Linux/macOS launcher
+-- test_system.py             # Diagnostic checks
+-- README.md                  # Documentation
`

## How It Works

1. **Upload**: Image uploaded via drag-drop or file selector; samples also available
2. **Forensics**: EXIF/metadata analysis, Error Level Analysis (ELA), 2D FFT spectrum, noise/texture/color analysis
3. **Dossier**: Metrics compiled into structured text for reasoning
4. **Analysis**: Sends to local LLM (Ollama) if available, else uses rule-based evaluator
5. **Results**: Verdict, confidence, breakdown, evidence, visualizations displayed in UI

## Running Locally

### Prerequisites
- Python 3.9+ installed
- (Optional) Ollama with qwen2.5-coder:3b: ollama pull qwen2.5-coder:3b then ollama run qwen2.5-coder:3b

### Quick Start
1. Install dependencies: pip install -r requirements.txt
2. (Optional) Start Ollama in separate terminal: ollama run qwen2.5-coder:3b
3. Start app: 
   - Windows: start.bat
   - Linux/macOS: ./start.sh or python backend/app.py
4. Open browser: http://127.0.0.1:8000
5. Upload image or test with samples

### Diagnostics
Run python test_system.py to verify dependencies, samples, and connectivity.

## Deployment

The app serves both API and static frontend from the FastAPI server. For local/deployment:
- Backend serves frontend at root / and static files at /static/
- All dependencies in requirements.txt
- Configuration via environment variables (OLLAMA_BASE_URL, OLLAMA_MODEL, HOST, PORT)

## Frontend Deployment (GitHub Pages) + Local Backend

The frontend can be deployed separately (GitHub Pages / any static host) while the backend keeps running on your PC.

What changed for split hosting:
- `frontend/app.js` has a configurable **Backend API Base URL** (Settings modal). Leave it empty for local same-origin use; set it to your backend URL when hosted separately.
- Backend binds to `0.0.0.0` and CORS allows all origins.
- `.github/workflows/deploy-frontend.yml` auto-deploys the `frontend/` folder to GitHub Pages on every push to `main` (when frontend files change).

Steps:
1. Push repo to GitHub: `git push origin main`
2. In GitHub repo: **Settings -> Pages -> Source: GitHub Actions** (one-time).
3. Workflow deploys `frontend/` automatically. Site: `https://<user>.github.io/REALORREEL/`
4. Make your local backend publicly reachable:
   - Simplest: `ngrok http 8000` or `cloudflared tunnel --url http://localhost:8000`
   - Or run backend on a server/VPS: `HOST=0.0.0.0 python backend/app.py`
5. Open deployed frontend -> **Settings** -> set **Backend API Base URL** to your tunnel/backend URL (e.g. `https://xxxx.ngrok-free.app`) -> Save.

Note: browser must reach the backend URL directly (HTTPS recommended since GitHub Pages is HTTPS; ngrok/cloudflared provide HTTPS automatically).

## Troubleshooting

- **Module errors**: Run pip install -r requirements.txt
- **Ollama not found**: System auto-falls back to rule-based engine; start Ollama if desired
- **Port in use**: Change PORT env var
- **Encoding issues on Windows**: Set PYTHONIOENCODING=utf-8 if needed

## Notes

Everything runs fully locally. The system is designed to work without internet connectivity after setup.
