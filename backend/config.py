import os

class Config:
    # Local Qwen2.5-Coder:3b AI Brain settings
    # Default to local Ollama running on user's PC
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
    
    # Optional OpenAI-compatible endpoint (e.g. LM Studio, vLLM, or Ollama /v1)
    OPENAI_COMPATIBLE_URL = os.getenv("OPENAI_COMPATIBLE_URL", "http://localhost:11434/v1")
    
    # Server settings
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Request timeouts
    AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "45"))
    
    # Forensic analysis tuning
    ELA_QUALITY = int(os.getenv("ELA_QUALITY", "90"))
    FFT_GRID_SPIKE_THRESHOLD = float(os.getenv("FFT_GRID_SPIKE_THRESHOLD", "4.0"))
