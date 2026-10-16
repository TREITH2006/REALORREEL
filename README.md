# RealOrReel - Image Authenticity Verification System

RealOrReel is a completely local, privacy-first image forensics system that analyzes uploaded images to determine if they are authentic camera-captured images (**REAL**) or AI-generated/synthetic media (**REEL**). It uses open-source computer vision techniques with optional local model reasoning, and automatically falls back to rule-based analysis when no local model is available.

**Everything runs on your PC. No images or analysis data leave your machine.**

---

## Overview

After installation the application runs entirely offline. All image processing happens locally. It works with or without a local model server - if none is running, the built-in forensic rule engine handles analysis automatically.

---

## Complete Project Structure

```
REALORREEL/
├── backend/                        # FastAPI backend
│   ├── __init__.py                 # Package marker
│   ├── app.py                      # FastAPI app + endpoints (/, /api/health, /api/analyze, /api/sample/{type})
│   ├── brain_client.py             # Local model client + deterministic fallback evaluator
│   ├── config.py                   # Config (endpoints, host, port, timeouts, thresholds)
│   ├── forensics.py                # Forensic extraction (EXIF, ELA, FFT, noise/texture)
│   └── samples/                    # Test sample images
│       ├── sample_ai.png           # AI-generated sample
│       └── sample_real.jpg         # Real camera photo sample
├── frontend/                       # Web UI (served by backend at /)
│   ├── app.js                      # Frontend logic + 3D holographic renderer
│   ├── index.html                  # UI structure
│   └── style.css                   # Styling
├── .github/workflows/
│   └── deploy-frontend.yml         # GitHub Pages frontend deployment workflow
├── requirements.txt                # Python dependencies
├── start.bat                       # Windows launcher (installs deps + starts + opens browser)
├── start.sh                        # Linux/macOS launcher
├── run_all.bat                     # Quick Windows script (backend + browser)
├── run_all.ps1                     # Quick PowerShell script (backend + browser)
├── test_system.py                  # Diagnostic test suite
├── QUICKSTART.txt                  # Quick run notes
├── .gitignore                      # Ignores venv/, __pycache__, .env, IDE files
└── README.md                       # This file
```

---

## How It Works (Core Flow)

```
USER (Browser Frontend)
   │  1. Upload picture (drag-drop / file picker / 1-click samples)
   ▼
FASTAPI BACKEND (local server, port 8000)
   │  2. Receives raw image bytes
   ▼
FORENSIC EXTRACTOR (open-source CV tools)
   │  3. Converts picture into quantitative codes/metrics:
   │     - EXIF / metadata provenance
   │     - Error Level Analysis (ELA)
   │     - 2D FFT frequency spectrum
   │     - Noise / texture / saturation stats
   │  4. Compiles metrics into a structured text dossier
   ▼
ANALYSIS BRAIN (local model via Ollama, if running)
   │  5. Reads dossier -> produces verdict, confidence,
   │     breakdown, key evidence, recommendation (JSON)
   │  (If model not running: rule-based evaluator gives the same
   │   verdict structure from the metrics automatically)
   ▼
FRONTEND DISPLAY
      6. Shows verdict (REAL / REEL / SUSPICIOUS), confidence gauge,
         ELA + FFT heatmaps, evidence list, full dossier
```

### Detection Signals Used

| Signal | What it checks |
|---|---|
| Camera hardware EXIF | Make/Model/Lens/ISO/Shutter presence |
| AI signatures | Generation-tool tags in metadata/software fields |
| ELA | Compression uniformity vs natural variance |
| 2D FFT | Periodic grid spikes from upsampling artifacts |
| Sensor noise | Natural CMOS noise (PRNU proxy) vs smoothing |
| Color stats | Saturation, kurtosis, channel correlations |

---

## Running Locally (VS Code Terminal)

### Prerequisites
- Python 3.9+
- (Optional) local model server for enhanced reasoning: `ollama pull qwen2.5-coder:3b`

### Commands

```bash
# 1. Go to project folder
cd C:\Users\adi86\Downloads\realorrell1\REALORREEL

# 2. Create/activate virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1          # PowerShell
# .\venv\Scripts\activate.bat        # CMD

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) start local model in a SEPARATE terminal
ollama run qwen2.5-coder:3b

# 5. Start the app (frontend + backend together)
python backend/app.py
```

Then open **http://127.0.0.1:8000** in your browser.

### One-Click Alternatives
- **Windows CMD**: `start.bat` (installs deps, starts server, opens browser)
- **Windows**: `run_all.bat` or `run_all.ps1`
- **Linux/macOS**: `./start.sh`

### Diagnostics
```bash
python test_system.py
```
Verifies dependencies, runs forensics on bundled samples, checks model connectivity.

### Stop
`Ctrl+C` in the terminal running the server.

---

## API Endpoints (Backend)

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves frontend UI |
| `/static/*` | GET | CSS/JS assets |
| `/api/health` | GET | Backend + model status |
| `/api/analyze` | POST | Upload image -> full forensic report |
| `/api/sample/{real\|ai}` | GET | Serve bundled test samples |
| `/docs` | GET | Auto-generated API docs |

Backend API Base URL (local): **`http://127.0.0.1:8000`**

---

## Configuration (Environment Variables)

| Variable | Default | Purpose |
|---|---|---|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local model endpoint |
| `OLLAMA_MODEL` | `qwen2.5-coder:3b` | Target model name |
| `AI_TIMEOUT_SECONDS` | `45` | Model request timeout |
| `ELA_QUALITY` | `90` | ELA recompression quality |
| `FFT_GRID_SPIKE_THRESHOLD` | `4.0` | FFT anomaly threshold |

Frontend settings (gear icon) let you change: Backend API Base URL, model endpoint, model name (saved in browser localStorage).

---

## Frontend Deployment (GitHub Pages) + Local Backend (Optional)

The frontend can be deployed separately while the backend keeps running on your PC.

- `frontend/app.js` has a configurable **Backend API Base URL** in Settings. Leave EMPTY for local use; set to your backend URL when hosted separately.
- `.github/workflows/deploy-frontend.yml` auto-deploys `frontend/` to GitHub Pages on pushes to `main`.

Steps:
1. Push to GitHub: `git push origin main`
2. Repo **Settings -> Pages -> Source: GitHub Actions** (one-time)
3. Site: `https://<user>.github.io/REALORREEL/`
4. Expose local backend: `ngrok http 8000` or `cloudflared tunnel --url http://localhost:8000`
5. Open deployed frontend -> **Settings** -> set Backend API Base URL -> Save

---

## Issues Faced & Fixes

| Issue | Cause | Fix |
|---|---|---|
| `UnicodeEncodeError: 'charmap' codec` when running tests | Windows console default encoding (cp1252) | Set `$env:PYTHONIOENCODING="utf-8"` before running, or use `start.bat` |
| `ERR_CONNECTION_REFUSED` at 127.0.0.1:8000 | Server not running / stopped | Start again: `python backend/app.py` |
| `ModuleNotFoundError: No module named 'config'` | Wrong working dir for imports | Always run from project root: `python backend/app.py` |
| `git push rejected (non-fast-forward)` | Remote had newer commits | `git pull --rebase` then `git push` |
| README/garbled characters in terminal | Old file was UTF-8 rendered as cp1252 | README rewritten clean; run with `PYTHONIOENCODING=utf-8` |
| Port already in use | Previous server instance still running | Stop python processes or set `PORT=8001` |
| 404 on `/api/config` | Endpoint never existed (harmless probe) | No action needed; core endpoints all return 200 |
| Model endpoint unreachable | Ollama not running | Optional - system auto-falls back to rule engine |

---

## Testing Status

- Python syntax: all backend modules compile clean
- Frontend JS: syntax valid
- Sample REAL image -> verdict **REAL**
- Sample AI image -> verdict **REEL**
- `/api/health` -> `healthy`
- `/` and `/static/*` -> `200 OK`

---

## Requirements (requirements.txt)

```
fastapi>=0.100.0
uvicorn>=0.22.0
python-multipart>=0.0.6
Pillow>=9.5.0
numpy>=1.24.0
opencv-python-headless>=4.7.0
requests>=2.28.0
```

---

## Notes

- Everything runs fully locally; designed to work without internet after setup.
- Local model server is fully optional - the rule engine produces complete verdicts on its own.
- Sample images are bundled for immediate 1-click testing.
