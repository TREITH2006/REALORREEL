import io
import base64
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance
from PIL.ExifTags import TAGS, GPSTAGS

AI_SIGNATURE_KEYWORDS = [
    "midjourney", "stable diffusion", "stablediffusion", "dall-e", "dalle", 
    "novelai", "comfyui", "automatic1111", "invokeai", "firefly", 
    "bing image creator", "flux", "sdxl", "civitai", "lora", "craiyon"
]

def analyze_metadata(image_bytes: bytes) -> dict:
    """Extract EXIF, container metadata, software tags, and hardware provenance."""
    img = Image.open(io.BytesIO(image_bytes))
    info = img.info or {}
    
    detected_ai_signatures = []
    
    # 1. Check container info (PNG text chunks, comments)
    for k, v in info.items():
        val_str = str(v).lower()
        for sig in AI_SIGNATURE_KEYWORDS:
            if sig in val_str:
                detected_ai_signatures.append(f"Found '{sig}' in metadata chunk '{k}'")

    exif_data = {}
    has_camera_hardware = False
    camera_make = None
    camera_model = None
    software_tag = None
    lens_model = None
    iso = None
    shutter_speed = None
    focal_length = None
    f_stop = None
    date_original = None

    try:
        raw_exif = img._getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                # Skip massive binary blocks
                if isinstance(value, (bytes, bytearray)):
                    continue
                exif_data[tag_name] = str(value)
                
            camera_make = exif_data.get("Make")
            camera_model = exif_data.get("Model")
            software_tag = exif_data.get("Software")
            lens_model = exif_data.get("LensModel")
            iso = exif_data.get("ISOSpeedRatings") or exif_data.get("PhotographicSensitivity")
            shutter_speed = exif_data.get("ExposureTime")
            focal_length = exif_data.get("FocalLength")
            f_stop = exif_data.get("FNumber")
            date_original = exif_data.get("DateTimeOriginal")

            if camera_make or camera_model:
                has_camera_hardware = True

            if software_tag:
                sw_lower = software_tag.lower()
                for sig in AI_SIGNATURE_KEYWORDS:
                    if sig in sw_lower:
                        detected_ai_signatures.append(f"Found '{sig}' in EXIF Software tag")
    except Exception:
        pass

    return {
        "format": img.format or "UNKNOWN",
        "mode": img.mode,
        "width": img.width,
        "height": img.height,
        "aspect_ratio": round(img.width / img.height, 3) if img.height else 1.0,
        "has_exif": bool(exif_data),
        "has_camera_hardware": has_camera_hardware,
        "camera_make": camera_make,
        "camera_model": camera_model,
        "software_tag": software_tag,
        "lens_model": lens_model,
        "iso": iso,
        "shutter_speed": shutter_speed,
        "focal_length": focal_length,
        "f_stop": f_stop,
        "date_original": date_original,
        "detected_ai_signatures": list(set(detected_ai_signatures)),
        "exif_summary": {k: exif_data[k] for k in list(exif_data.keys())[:12]}
    }

def compute_ela(image_bytes: bytes, quality: int = 90) -> dict:
    """
    Error Level Analysis (ELA).
    Identifies variations in compression degradation across the image.
    Real photos exhibit uniform, texture-conforming noise.
    AI images and composite edits often exhibit localized compression discontinuities or artificial uniformity.
    """
    original = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Save as temp jpeg in memory
    buffer = io.BytesIO()
    original.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)
    
    # Calculate difference
    ela_im = ImageChops.difference(original, resaved)
    extrema = ela_im.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
        
    scale_factor = 255.0 / max_diff
    ela_enhanced = ImageEnhance.Brightness(ela_im).enhance(scale_factor * 0.85)
    
    ela_arr = np.array(ela_im).astype(np.float32)
    mean_error = float(np.mean(ela_arr))
    std_error = float(np.std(ela_arr))
    
    # Encode preview
    preview_buf = io.BytesIO()
    ela_enhanced.save(preview_buf, format='JPEG', quality=85)
    preview_base64 = base64.b64encode(preview_buf.getvalue()).decode('utf-8')
    
    return {
        "mean_error": round(mean_error, 2),
        "std_error": round(std_error, 2),
        "max_diff": int(max_diff),
        "preview_base64": f"data:image/jpeg;base64,{preview_base64}"
    }

def compute_fft_spectrum(image_bytes: bytes) -> dict:
    """
    2D Fast Fourier Transform analysis.
    Identifies periodic grid artifacts and high-frequency energy anomalies
    caused by transposed convolution upsampling in generative diffusion / GAN models.
    """
    img_pil = Image.open(io.BytesIO(image_bytes)).convert('L')
    img_gray = np.array(img_pil)
    
    # Standardize to 512x512 for consistent frequency spatial analysis
    if img_gray.shape[0] != 512 or img_gray.shape[1] != 512:
        img_gray = cv2.resize(img_gray, (512, 512), interpolation=cv2.INTER_AREA)
        
    f = np.fft.fft2(img_gray)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-9)
    
    # Normalize for visual preview
    norm_spec = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    colored_spec = cv2.applyColorMap(norm_spec, cv2.COLORMAP_VIRIDIS)
    
    # Energy distribution
    h, w = magnitude_spectrum.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    low_freq_mask = dist_from_center < 40
    high_freq_mask = dist_from_center >= 140
    
    low_freq_energy = float(np.mean(magnitude_spectrum[low_freq_mask]))
    high_freq_energy = float(np.mean(magnitude_spectrum[high_freq_mask]))
    hf_to_lf_ratio = round(high_freq_energy / (low_freq_energy + 1e-9), 4)
    
    # Detect periodic spikes in high-frequency regions
    outer_mag = magnitude_spectrum.copy()
    outer_mag[dist_from_center < 70] = 0
    peak_val = float(np.max(outer_mag))
    mean_val = float(np.mean(outer_mag[dist_from_center >= 70]))
    spike_prominence = round((peak_val - mean_val) / (np.std(outer_mag[dist_from_center >= 70]) + 1e-9), 3)
    
    # Encode preview
    _, spec_buf = cv2.imencode('.jpg', colored_spec, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    spec_base64 = base64.b64encode(spec_buf).decode('utf-8')
    
    return {
        "high_to_low_freq_ratio": hf_to_lf_ratio,
        "frequency_spike_prominence": spike_prominence,
        "has_periodic_grid_artifacts": bool(spike_prominence > 4.2),
        "preview_base64": f"data:image/jpeg;base64,{spec_base64}"
    }

def compute_noise_and_texture(image_bytes: bytes) -> dict:
    """Analyze noise residuals, sharpness variance, and color saturation characteristics."""
    img_bgr = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if img_bgr is None:
        img_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Laplacian variance (overall sharpness)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_var = float(laplacian.var())
    
    # Sensor noise proxy via high-pass median residual
    denoised = cv2.medianBlur(gray, 3)
    noise_residual = cv2.absdiff(gray, denoised)
    noise_mean = float(np.mean(noise_residual))
    noise_std = float(np.std(noise_residual))
    
    # Color distribution & saturation
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    mean_saturation = float(np.mean(sat))
    sat_std = float(np.std(sat))
    saturation_kurtosis = float(np.mean(((sat - mean_saturation) / (sat_std + 1e-9))**4))
    
    # Color channel correlations
    r, g, b = img_bgr[:, :, 2], img_bgr[:, :, 1], img_bgr[:, :, 0]
    corr_rg = float(np.corrcoef(r.flatten(), g.flatten())[0, 1])
    corr_rb = float(np.corrcoef(r.flatten(), b.flatten())[0, 1])
    
    return {
        "laplacian_variance": round(laplacian_var, 2),
        "noise_residual_mean": round(noise_mean, 2),
        "noise_residual_std": round(noise_std, 2),
        "mean_saturation": round(mean_saturation, 2),
        "saturation_kurtosis": round(saturation_kurtosis, 2),
        "channel_correlation_rg": round(corr_rg, 3),
        "channel_correlation_rb": round(corr_rb, 3)
    }

def run_full_forensics(image_bytes: bytes) -> dict:
    """Execute complete suite of open-source forensic detectors."""
    meta = analyze_metadata(image_bytes)
    ela = compute_ela(image_bytes)
    fft = compute_fft_spectrum(image_bytes)
    texture = compute_noise_and_texture(image_bytes)
    
    heuristic_signals = []
    
    if meta["detected_ai_signatures"]:
        for sig in meta["detected_ai_signatures"]:
            heuristic_signals.append(f"CRITICAL: {sig}")
            
    if meta["has_camera_hardware"]:
        heuristic_signals.append(f"AUTHENTICITY_SIGNAL: Camera hardware identified ({meta['camera_make']} {meta['camera_model']})")
    else:
        heuristic_signals.append("SUSPICIOUS: Missing all physical camera hardware EXIF tags (Make, Model, Lens, ISO, Shutter)")
        
    if fft["has_periodic_grid_artifacts"]:
        heuristic_signals.append(f"AI_ANOMALY: High periodic frequency spikes detected (prominence {fft['frequency_spike_prominence']} > 4.2), indicating upsampling grid artifacts typical of diffusion/GAN architectures")
    else:
        heuristic_signals.append(f"CLEAN_SPECTRUM: Frequency spectrum follows natural optical decay (prominence {fft['frequency_spike_prominence']})")
        
    if ela["mean_error"] < 0.2:
        heuristic_signals.append("AI_ANOMALY: Zero/lossless compression error (<0.2), typical of direct digital synthetics or vector graphics")
    elif ela["mean_error"] > 16.0:
        heuristic_signals.append("SUSPICIOUS: High compression discrepancy across regions, indicating possible localized manipulation or inpainting")
    else:
        heuristic_signals.append(f"NATURAL_COMPRESSION: ELA error rate within natural photographic range ({ela['mean_error']})")
        
    if texture["mean_saturation"] > 140 and texture["saturation_kurtosis"] > 5.0:
        heuristic_signals.append("AI_ANOMALY: Hyper-saturated color distribution with extreme kurtosis, commonly observed in generative art stylizations")

    return {
        "metadata": meta,
        "ela": ela,
        "fft": fft,
        "texture": texture,
        "heuristic_signals": heuristic_signals
    }

def build_qwen_dossier(forensics_data: dict) -> str:
    """
    Translates quantitative forensic data into a structured dossier formatted
    specifically for the Qwen2.5-Coder:3b AI Brain to understand and evaluate.
    """
    meta = forensics_data["metadata"]
    ela = forensics_data["ela"]
    fft = forensics_data["fft"]
    tex = forensics_data["texture"]
    signals = forensics_data["heuristic_signals"]
    
    dossier = f"""### IMAGE FORENSIC INSPECTION DOSSIER ###
[FILE SPECIFICATIONS]
- Format: {meta['format']} | Dimensions: {meta['width']}x{meta['height']} | Aspect Ratio: {meta['aspect_ratio']}
- Color Mode: {meta['mode']}

[METADATA & HARDWARE PROVENANCE]
- Has EXIF: {'YES' if meta['has_exif'] else 'NO'}
- Physical Camera Hardware Detected: {'YES (' + str(meta['camera_make']) + ' ' + str(meta['camera_model']) + ')' if meta['has_camera_hardware'] else 'NO (Missing)'}
- Lens Model: {meta['lens_model'] or 'None'}
- Exposure / ISO / Shutter: ISO {meta['iso'] or 'N/A'}, F/{meta['f_stop'] or 'N/A'}, Shutter: {meta['shutter_speed'] or 'N/A'}
- Software Tag: {meta['software_tag'] or 'None'}
- Known AI Signatures Detected in Chunks: {', '.join(meta['detected_ai_signatures']) if meta['detected_ai_signatures'] else 'None'}

[ERROR LEVEL ANALYSIS (ELA) METRICS]
- Mean Compression Difference: {ela['mean_error']}
- Standard Deviation: {ela['std_error']}
- Max Difference: {ela['max_diff']}
- Evaluation: Natural photographic captures typically exhibit gradual texture-correlated compression variation. Lossless synthetic renders show near-zero error (<0.2), while spliced or in-painted composites trigger high error spikes (>16.0).

[2D FAST FOURIER TRANSFORM (FFT) FREQUENCY SPECTRUM]
- High-to-Low Frequency Energy Ratio: {fft['high_to_low_freq_ratio']}
- Periodic Grid Spike Prominence: {fft['frequency_spike_prominence']}
- Periodic Grid Artifacts Detected: {'YES (Synthetic Upsampling / Convolution Signature)' if fft['has_periodic_grid_artifacts'] else 'NO (Natural Optical Falloff)'}

[TEXTURE, NOISE & COLOR DYNAMICS]
- Laplacian Texture Variance: {tex['laplacian_variance']} (measures micro-edge sharpness consistency)
- Sensor Noise Residual Mean: {tex['noise_residual_mean']} (CMOS sensor PRNU proxy)
- Noise Residual Std: {tex['noise_residual_std']}
- Color Saturation Mean: {tex['mean_saturation']} / 255
- Saturation Kurtosis: {tex['saturation_kurtosis']}
- Color Channel Correlation (R-G / R-B): {tex['channel_correlation_rg']} / {tex['channel_correlation_rb']}

[DETECTED HEURISTIC SIGNALS]
{chr(10).join('- ' + s for s in signals)}
"""
    return dossier
