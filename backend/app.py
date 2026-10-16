import os
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
SAMPLES_DIR = BASE_DIR / "samples"
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from forensics import run_full_forensics, build_qwen_dossier
from brain_client import analyze_with_brain, check_brain_status

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("realorrell.app")

app = FastAPI(
    title="RealOrReel - AI vs Original Image Verifier",
    description="Local forensic verification system powered by open-source computer vision and local Qwen2.5-Coder:3b AI Brain",
    version="1.0.0"
)

# Enable CORS for local dev flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static directory if exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>RealOrReel backend active. Frontend not found.</h1>", status_code=200)

@app.get("/api/health")
async def health_check(ollama_url: str = Config.OLLAMA_BASE_URL, model_name: str = Config.OLLAMA_MODEL):
    """Check backend operational health and ping local Qwen brain."""
    brain_status = check_brain_status(base_url=ollama_url, model=model_name)
    return {
        "status": "healthy",
        "service": "realorrell-forensics",
        "version": "1.0.0",
        "brain": brain_status
    }

@app.post("/api/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    ollama_url: str = Form(Config.OLLAMA_BASE_URL),
    model_name: str = Form(Config.OLLAMA_MODEL)
):
    """
    Core verification pipeline:
    1. Read uploaded image bytes
    2. Extract multi-modal forensic features (Metadata, ELA, 2D FFT, Noise, Color)
    3. Format quantitative features into a semantic dossier
    4. Query local Qwen2.5-Coder:3b AI Brain for verdict and reasoning
    5. Return comprehensive inspection report and visual heatmaps
    """
    logger.info(f"Received file: {file.filename} (content_type: {file.content_type})")
    
    # Read image contents
    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    # 1. Execute Open-Source Forensics
    try:
        forensics_data = run_full_forensics(contents)
    except Exception as e:
        logger.error(f"Forensic extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=f"Unable to process image format: {str(e)}")

    # 2. Translate to Qwen-Understandable Semantic Dossier
    dossier = build_qwen_dossier(forensics_data)
    logger.info("Forensic dossier constructed successfully. Forwarding to AI Brain...")

    # 3. Query Qwen2.5-Coder:3b AI Brain
    ai_verdict = analyze_with_brain(
        dossier=dossier,
        forensics_data=forensics_data,
        base_url=ollama_url,
        model=model_name
    )

    # 4. Structure the final response
    meta = forensics_data["metadata"]
    ela = forensics_data["ela"]
    fft = forensics_data["fft"]
    tex = forensics_data["texture"]

    return {
        "success": True,
        "filename": file.filename,
        "verdict": ai_verdict.get("verdict", "SUSPICIOUS"),
        "confidence": ai_verdict.get("confidence", 70),
        "summary": ai_verdict.get("summary", "Analysis completed."),
        "forensic_breakdown": ai_verdict.get("forensic_breakdown", {}),
        "key_evidence": ai_verdict.get("key_evidence", []),
        "recommendation": ai_verdict.get("recommendation", "Review secondary verification signals."),
        "brain_info": {
            "active": ai_verdict.get("brain_active", False),
            "source": ai_verdict.get("_source", "local"),
            "notice": ai_verdict.get("brain_notice")
        },
        "visualizations": {
            "ela_preview": ela["preview_base64"],
            "fft_preview": fft["preview_base64"]
        },
        "quantitative_metrics": {
            "format": meta["format"],
            "resolution": f"{meta['width']}x{meta['height']}",
            "has_camera_hardware": meta["has_camera_hardware"],
            "camera_model": f"{meta['camera_make'] or ''} {meta['camera_model'] or ''}".strip() or "None",
            "detected_ai_signatures": meta["detected_ai_signatures"],
            "ela_mean_error": ela["mean_error"],
            "fft_high_to_low_ratio": fft["high_to_low_freq_ratio"],
            "fft_grid_spike_prominence": fft["frequency_spike_prominence"],
            "has_periodic_grid_artifacts": fft["has_periodic_grid_artifacts"],
            "laplacian_variance": tex["laplacian_variance"],
            "sensor_noise_mean": tex["noise_residual_mean"],
            "mean_saturation": tex["mean_saturation"]
        },
        "semantic_dossier_text": dossier
    }

@app.get("/api/sample/{sample_type}")
async def get_sample(sample_type: str):
    """Serve sample images for 1-click testing."""
    sample_file = SAMPLES_DIR / f"sample_{sample_type}.jpg"
    if not sample_file.exists():
        sample_file = SAMPLES_DIR / f"sample_{sample_type}.png"
        
    if not sample_file.exists():
        raise HTTPException(status_code=404, detail="Sample image not found.")
        
    return FileResponse(str(sample_file))

if __name__ == "__main__":
    import uvicorn
    print(f"Starting RealOrReel server at http://{Config.HOST}:{Config.PORT}")
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=True)
