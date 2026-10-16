import json
import logging
import requests
from config import Config

logger = logging.getLogger("realorrell.brain")

SYSTEM_PROMPT = """You are RealOrReel AI Brain, a forensic media analyst and AI detection specialist.
Your task is to analyze a quantitative Image Forensic Inspection Dossier extracted by open-source computer vision detectors and determine whether an image is:
- "REAL" (authentic physical camera capture or organic graphic)
- "REEL" (AI-generated image, synthetic diffusion, GAN, or deepfake)
- "SUSPICIOUS" (tampered, inpainted, or hybrid)

You must evaluate:
1. Metadata & Hardware Provenance: Presence of real camera hardware tags (Make, Model, Lens, ISO, Shutter) vs known AI signatures (Midjourney, Stable Diffusion, DALL-E, ComfyUI) or completely scrubbed container headers.
2. Error Level Analysis (ELA): Natural non-uniform compression error vs artificial uniformity (<2.5) or sharp inpainting boundaries.
3. Frequency Domain (2D FFT): Natural optical decay vs high-frequency periodic grid spikes caused by transposed convolution upsampling in generative networks.
4. Noise & Texture Dynamics: Natural CMOS sensor pattern noise (PRNU) vs synthetic blur/smoothing and hyper-saturated color profiles.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "verdict": "REAL" | "REEL" | "SUSPICIOUS",
  "confidence": 85,
  "summary": "Concise 1-2 sentence decisive verdict explanation.",
  "forensic_breakdown": {
    "metadata_provenance": "Detailed assessment of camera provenance and software tags.",
    "compression_analysis": "Evaluation of ELA error rate and compression uniformity.",
    "frequency_spectrum": "Assessment of 2D FFT spectral decay and upsampling grid artifacts.",
    "noise_texture": "Evaluation of sensor noise, edge sharpness, and color saturation dynamics."
  },
  "key_evidence": [
    "Key concrete evidence point 1",
    "Key concrete evidence point 2",
    "Key concrete evidence point 3"
  ],
  "recommendation": "Actionable verification advice."
}

Do not include any conversational filler, markdown fences, or text outside the JSON object.
"""

def query_qwen_ollama(dossier: str, base_url: str = Config.OLLAMA_BASE_URL, model: str = Config.OLLAMA_MODEL) -> dict:
    """Send forensic dossier to local Qwen2.5-Coder:3b via Ollama API."""
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this image forensic dossier and provide your JSON verdict:\n\n{dossier}"}
        ],
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }
    
    response = requests.post(url, json=payload, timeout=Config.AI_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    
    # Ollama returns output in message.content
    content = data.get("message", {}).get("content", "")
    return json.loads(content)

def query_qwen_openai_compatible(dossier: str, endpoint_url: str = Config.OPENAI_COMPATIBLE_URL, model: str = Config.OLLAMA_MODEL) -> dict:
    """Send forensic dossier via OpenAI-compatible endpoint (Ollama /v1, LM Studio, etc.)."""
    url = f"{endpoint_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this image forensic dossier and provide your JSON verdict:\n\n{dossier}"}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(url, json=payload, timeout=Config.AI_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)

def fallback_forensic_evaluator(forensics_data: dict) -> dict:
    """
    Intelligent deterministic forensic evaluator that runs if local Ollama
    is unreachable. Ensures application operates seamlessly even before Qwen is launched.
    """
    meta = forensics_data["metadata"]
    ela = forensics_data["ela"]
    fft = forensics_data["fft"]
    tex = forensics_data["texture"]
    
    score_reel = 0
    score_real = 0
    evidence = []
    
    # 1. Metadata check
    if meta["detected_ai_signatures"]:
        score_reel += 60
        evidence.append(f"Direct AI software generator signature identified: {', '.join(meta['detected_ai_signatures'])}")
    elif meta["has_camera_hardware"]:
        score_real += 40
        evidence.append(f"Authentic physical camera hardware verified: {meta['camera_make']} {meta['camera_model']}")
    else:
        score_reel += 15
        evidence.append("Missing physical camera sensor provenance (no camera make/model or lens tags)")

    # 2. FFT Periodic Artifacts
    if fft["has_periodic_grid_artifacts"]:
        score_reel += 35
        evidence.append(f"Periodic frequency grid spikes detected (prominence {fft['frequency_spike_prominence']}), typical of diffusion/GAN transposed convolution upsamplers")
    else:
        score_real += 25
        evidence.append("Frequency spectrum exhibits natural optical decay without periodic upsampling grid spikes")

    # 3. ELA Error Level Analysis
    if ela["mean_error"] < 2.5:
        score_reel += 25
        evidence.append(f"Abnormally low/uniform ELA compression variance ({ela['mean_error']}), consistent with direct synthetic rendering")
    elif ela["mean_error"] > 14.0:
        score_reel += 20
        evidence.append(f"High compression error discrepancy across regions ({ela['mean_error']}), indicating potential localized inpainting or splicing")
    else:
        score_real += 20
        evidence.append(f"Error Level Analysis within typical natural photographic range (mean error: {ela['mean_error']})")

    # 4. Color & Texture dynamics
    if tex["mean_saturation"] > 140 and tex["saturation_kurtosis"] > 4.5:
        score_reel += 15
        evidence.append("Hyper-saturated color distribution with elevated kurtosis, characteristic of generative art stylizations")
    if tex["noise_residual_mean"] > 12.0:
        score_real += 15
        evidence.append("Natural CMOS sensor pattern noise (PRNU) residual detected in high-frequency band")

    total = score_reel + score_real
    if total == 0:
        total = 1
    reel_pct = int(round((score_reel / total) * 100))
    
    if reel_pct >= 60:
        verdict = "REEL"
        confidence = min(98, max(65, reel_pct))
        summary = "Image exhibits significant statistical, frequency, or metadata signatures characteristic of AI-generated synthetic media."
    elif reel_pct <= 40:
        verdict = "REAL"
        confidence = min(98, max(65, 100 - reel_pct))
        summary = "Image displays physical camera sensor noise, authentic frequency decay, and camera provenance consistent with an original camera capture."
    else:
        verdict = "SUSPICIOUS"
        confidence = 60
        summary = "Image exhibits conflicting forensic signals. It may be an altered original photo, compressed web media, or hybrid inpainting."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "summary": summary,
        "forensic_breakdown": {
            "metadata_provenance": f"Camera hardware: {'Verified (' + str(meta['camera_make']) + ')' if meta['has_camera_hardware'] else 'Missing'}. AI signatures: {len(meta['detected_ai_signatures'])} detected.",
            "compression_analysis": f"Mean ELA error of {ela['mean_error']} with max difference {ela['max_diff']}.",
            "frequency_spectrum": f"2D FFT high-to-low ratio of {fft['high_to_low_freq_ratio']} with grid spike prominence of {fft['frequency_spike_prominence']}.",
            "noise_texture": f"Laplacian variance {tex['laplacian_variance']}, sensor noise mean {tex['noise_residual_mean']}, saturation mean {tex['mean_saturation']}."
        },
        "key_evidence": evidence[:4],
        "recommendation": "Inspect camera EXIF metadata and frequency grid peaks for corroborating secondary proof.",
        "_source": "forensic_rule_engine (Qwen brain offline or standby)"
    }

def analyze_with_brain(dossier: str, forensics_data: dict, base_url: str = Config.OLLAMA_BASE_URL, model: str = Config.OLLAMA_MODEL) -> dict:
    """
    Attempts to query the local Qwen2.5-Coder:3b AI Brain.
    Gracefully falls back to deterministic forensic engine if Qwen is not currently running.
    """
    # 1. Try Ollama native chat endpoint
    try:
        logger.info(f"Connecting to Qwen2.5-Coder:3b at {base_url} (model: {model})...")
        result = query_qwen_ollama(dossier, base_url=base_url, model=model)
        result["_source"] = f"qwen2.5-coder:3b ({base_url})"
        result["brain_active"] = True
        return result
    except Exception as e_ollama:
        logger.warning(f"Ollama native endpoint failed: {e_ollama}. Trying OpenAI compatible endpoint...")
        
    # 2. Try OpenAI compatible endpoint (Ollama /v1 or LM Studio)
    try:
        result = query_qwen_openai_compatible(dossier, endpoint_url=Config.OPENAI_COMPATIBLE_URL, model=model)
        result["_source"] = f"qwen2.5-coder:3b ({Config.OPENAI_COMPATIBLE_URL})"
        result["brain_active"] = True
        return result
    except Exception as e_openai:
        logger.warning(f"OpenAI compatible endpoint failed: {e_openai}. Using forensic engine fallback.")
        
    # 3. Fallback to forensic rule engine
    result = fallback_forensic_evaluator(forensics_data)
    result["brain_active"] = False
    result["brain_notice"] = f"Local Qwen brain at '{base_url}' was not reachable. Evaluated using built-in forensic detector engine. Start Ollama with: 'ollama run {model}' to activate live neural reasoning."
    return result

def check_brain_status(base_url: str = Config.OLLAMA_BASE_URL, model: str = Config.OLLAMA_MODEL) -> dict:
    """Check if local Qwen brain is running and available."""
    try:
        # Check Ollama tags
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            has_qwen = any(model.lower() in name.lower() for name in model_names)
            return {
                "online": True,
                "endpoint": base_url,
                "target_model": model,
                "model_available": has_qwen,
                "installed_models": model_names
            }
    except Exception:
        pass
        
    return {
        "online": False,
        "endpoint": base_url,
        "target_model": model,
        "model_available": False,
        "hint": f"To start your local AI brain, run: ollama run {model}"
    }
