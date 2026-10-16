#!/usr/bin/env python3
"""
RealOrReel Diagnostic & Sanity Test Suite
Validates dependencies, forensic feature extraction, and Qwen AI Brain connectivity.
"""

import sys
import os
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "backend"))

print("=" * 60)
print("       REALORREEL DIAGNOSTIC TEST SUITE")
print("=" * 60)

# 1. Dependency Check
print("\n[1/3] Testing Core Dependencies...")
modules = [
    ("PIL", "Pillow"),
    ("cv2", "OpenCV"),
    ("numpy", "NumPy"),
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("requests", "Requests")
]

all_deps_ok = True
for mod_name, label in modules:
    try:
        __import__(mod_name)
        print(f"  ✓ {label:<10} : Available")
    except ImportError:
        print(f"  ✗ {label:<10} : MISSING (run: pip install -r requirements.txt)")
        all_deps_ok = False

if not all_deps_ok:
    print("\nPlease install missing requirements before continuing.")
    sys.exit(1)

# 2. Test Forensic Pipeline on Sample Images
print("\n[2/3] Validating Open-Source Forensic Engine...")
from forensics import run_full_forensics, build_qwen_dossier
from brain_client import fallback_forensic_evaluator, check_brain_status
from config import Config

real_sample_path = BASE_DIR / "backend" / "samples" / "sample_real.jpg"
ai_sample_path = BASE_DIR / "backend" / "samples" / "sample_ai.png"

if real_sample_path.exists():
    with open(real_sample_path, "rb") as f:
        f_real = run_full_forensics(f.read())
        v_real = fallback_forensic_evaluator(f_real)
        print(f"  ✓ Sample Real Image  -> Verdict: {v_real['verdict']} (Confidence: {v_real['confidence']}%)")
        print(f"    Camera Hardware: {f_real['metadata']['camera_make']} {f_real['metadata']['camera_model']}")
        print(f"    ELA Mean: {f_real['ela']['mean_error']} | FFT Grid Prominence: {f_real['fft']['frequency_spike_prominence']}")
else:
    print("  ✗ sample_real.jpg not found")

if ai_sample_path.exists():
    with open(ai_sample_path, "rb") as f:
        f_ai = run_full_forensics(f.read())
        v_ai = fallback_forensic_evaluator(f_ai)
        print(f"  ✓ Sample AI Image    -> Verdict: {v_ai['verdict']} (Confidence: {v_ai['confidence']}%)")
        print(f"    AI Signatures: {f_ai['metadata']['detected_ai_signatures']}")
        print(f"    ELA Mean: {f_ai['ela']['mean_error']} | FFT Grid Prominence: {f_ai['fft']['frequency_spike_prominence']}")
else:
    print("  ✗ sample_ai.png not found")

# 3. Check Local Qwen AI Brain Status
print("\n[3/3] Checking Connection to Qwen2.5-Coder:3b Brain...")
brain_status = check_brain_status(Config.OLLAMA_BASE_URL, Config.OLLAMA_MODEL)
if brain_status.get("online"):
    print(f"  ✓ Ollama endpoint online at {Config.OLLAMA_BASE_URL}")
    if brain_status.get("model_available"):
        print(f"  ✓ Target model '{Config.OLLAMA_MODEL}' is ready!")
    else:
        print(f"  ! Model '{Config.OLLAMA_MODEL}' not found in Ollama library.")
        print(f"    Installed models: {brain_status.get('installed_models', [])}")
        print(f"    To install run: ollama run {Config.OLLAMA_MODEL}")
else:
    print(f"  ! Local Ollama not currently running on {Config.OLLAMA_BASE_URL}.")
    print(f"    RealOrReel will automatically use its built-in forensic rules until you launch:")
    print(f"        ollama run {Config.OLLAMA_MODEL}")

print("\n" + "=" * 60)
print("Diagnostic Complete! Launch the web app by running:")
print("    python backend/app.py")
print("=" * 60 + "\n")
