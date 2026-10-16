/**
 * RealOrReel - 3D Holographic Forensic Verification Engine
 * Frontend Controller & 3D Interactive Picture Renderer
 */

// Configuration State
const state = {
  apiBase: (localStorage.getItem('realorrell_api_base') || '').replace(/\/$/, ''),
  ollamaUrl: localStorage.getItem('realorrell_ollama_url') || 'http://localhost:11434',
  modelName: localStorage.getItem('realorrell_model_name') || 'qwen2.5-coder:3b',
  currentFile: null,
  currentImageBitmap: null,
  isScanning: false,
  brainOnline: false,
  lastVerdict: null,
};

// DOM Elements
const elements = {
  canvas: document.getElementById('stageCanvas'),
  stageWrapper: document.getElementById('stageWrapper'),
  stagePlaceholder: document.getElementById('stagePlaceholder'),
  laserScanner: document.getElementById('laserScanner'),
  hudStatus: document.getElementById('hudStatus'),
  hudRes: document.getElementById('hudRes'),
  hudFps: document.getElementById('hudFps'),
  hudAngle: document.getElementById('hudAngle'),
  hudTarget: document.getElementById('hudTarget'),
  
  dropzone: document.getElementById('dropzone'),
  fileInput: document.getElementById('fileInput'),
  sampleRealBtn: document.getElementById('sampleRealBtn'),
  sampleAiBtn: document.getElementById('sampleAiBtn'),
  analyzeBtn: document.getElementById('analyzeBtn'),
  analyzeBtnText: document.getElementById('analyzeBtnText'),
  resetCamBtn: document.getElementById('resetCamBtn'),

  brainStatusPill: document.getElementById('brainStatusPill'),
  brainStatusText: document.getElementById('brainStatusText'),
  settingsBtn: document.getElementById('settingsBtn'),
  settingsModal: document.getElementById('settingsModal'),
  closeSettingsBtn: document.getElementById('closeSettingsBtn'),
  saveSettingsBtn: document.getElementById('saveSettingsBtn'),
  apiBaseInput: document.getElementById('apiBaseInput'),
  ollamaUrlInput: document.getElementById('ollamaUrlInput'),
  modelNameInput: document.getElementById('modelNameInput'),

  resultsSection: document.getElementById('resultsSection'),
  verdictCard: document.getElementById('verdictCard'),
  verdictMainBadge: document.getElementById('verdictMainBadge'),
  verdictSummaryText: document.getElementById('verdictSummaryText'),
  gaugeBar: document.getElementById('gaugeBar'),
  confidenceValue: document.getElementById('confidenceValue'),
  brainAttributionText: document.getElementById('brainAttributionText'),

  elaImg: document.getElementById('elaImg'),
  fftImg: document.getElementById('fftImg'),
  origImg: document.getElementById('origImg'),

  mCamera: document.getElementById('mCamera'),
  mEla: document.getElementById('mEla'),
  mFftSpike: document.getElementById('mFftSpike'),
  mNoise: document.getElementById('mNoise'),
  mSharpness: document.getElementById('mSharpness'),
  mSaturation: document.getElementById('mSaturation'),
  evidenceList: document.getElementById('evidenceList'),

  rMeta: document.getElementById('rMeta'),
  rEla: document.getElementById('rEla'),
  rFft: document.getElementById('rFft'),
  rNoise: document.getElementById('rNoise'),
  recommendationText: document.getElementById('recommendationText'),
  toggleDossierBtn: document.getElementById('toggleDossierBtn'),
  rawDossierBox: document.getElementById('rawDossierBox'),
  rawDossierPre: document.getElementById('rawDossierPre')
};

/* =====================================================================
   1. HIGH-PERFORMANCE 3D INTERACTIVE PICTURE RENDERER (Perspective Engine)
   ===================================================================== */
class Holographic3DStage {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    
    // 3D Camera / Orientation
    this.rotX = 0.15; // pitch
    this.rotY = -0.25; // yaw
    this.targetRotX = 0.15;
    this.targetRotY = -0.25;
    this.baseDistance = 600;
    
    // Mouse tracking
    this.isDragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;

    // Ambient floating 3D cyber particles
    this.particleCount = 50;
    this.particles = [];
    this.initParticles();

    // FPS Counter
    this.lastTime = performance.now();
    this.frameCount = 0;
    this.currentFps = 60;

    // Picture card state
    this.image = null;
    this.imageAspect = 1.0;
    this.scanProgress = 0;
    this.glowColor = '#00f2fe';

    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.bindEvents();
    this.animate();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      this.particles.push({
        x: (Math.random() - 0.5) * 500,
        y: (Math.random() - 0.5) * 350,
        z: (Math.random() - 0.5) * 500,
        size: Math.random() * 2 + 1,
        speed: Math.random() * 0.4 + 0.2,
        alpha: Math.random() * 0.7 + 0.3
      });
    }
  }

  bindEvents() {
    const wrapper = this.canvas.parentElement;

    // Mouse movement for parallax tilt
    wrapper.addEventListener('mousemove', (e) => {
      const rect = wrapper.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / rect.width - 0.5;
      const ny = (e.clientY - rect.top) / rect.height - 0.5;
      
      if (!this.isDragging) {
        this.targetRotY = nx * 0.7;
        this.targetRotX = -ny * 0.6;
      } else {
        const dx = e.clientX - this.lastMouseX;
        const dy = e.clientY - this.lastMouseY;
        this.targetRotY += dx * 0.008;
        this.targetRotX += dy * 0.008;
        this.lastMouseX = e.clientX;
        this.lastMouseY = e.clientY;
      }
    });

    wrapper.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    wrapper.addEventListener('mouseleave', () => {
      if (!this.isDragging) {
        this.targetRotX = 0.1;
        this.targetRotY = 0.0;
      }
    });
  }

  resetCamera() {
    this.targetRotX = 0.15;
    this.targetRotY = -0.25;
  }

  setImage(img) {
    this.image = img;
    this.imageAspect = img.width / img.height;
    elements.stagePlaceholder.classList.add('hidden');
    elements.hudTarget.textContent = `TARGET: ${img.width}x${img.height} LOADED`;
    elements.hudRes.textContent = `${img.width}x${img.height}`;
  }

  project(x, y, z) {
    // 3D Rotation (Pitch around X, Yaw around Y)
    const cosY = Math.cos(this.rotY);
    const sinY = Math.sin(this.rotY);
    const cosX = Math.cos(this.rotX);
    const sinX = Math.sin(this.rotX);

    // Rotate around Y
    const x1 = x * cosY - z * sinY;
    const z1 = z * cosY + x * sinY;

    // Rotate around X
    const y2 = y * cosX - z1 * sinX;
    const z2 = z1 * cosX + y * sinX;

    // Perspective projection
    const fov = 420;
    const distance = z2 + this.baseDistance;
    if (distance <= 10) return null;

    const scale = fov / distance;
    const projX = this.width / 2 + x1 * scale;
    const projY = this.height / 2 + y2 * scale;

    return { x: projX, y: projY, scale, z: z2 };
  }

  drawGrid() {
    const ctx = this.ctx;
    const size = 320;
    const step = 40;
    const yPos = 140; // Ground plane

    ctx.save();
    ctx.lineWidth = 1;

    for (let i = -size; i <= size; i += step) {
      // Lines along Z
      const p1 = this.project(i, yPos, -size);
      const p2 = this.project(i, yPos, size);
      if (p1 && p2) {
        const grad = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
        grad.addColorStop(0, 'rgba(56, 189, 248, 0)');
        grad.addColorStop(0.5, 'rgba(56, 189, 248, 0.25)');
        grad.addColorStop(1, 'rgba(56, 189, 248, 0)');
        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }

      // Lines along X
      const p3 = this.project(-size, yPos, i);
      const p4 = this.project(size, yPos, i);
      if (p3 && p4) {
        const grad = ctx.createLinearGradient(p3.x, p3.y, p4.x, p4.y);
        grad.addColorStop(0, 'rgba(56, 189, 248, 0)');
        grad.addColorStop(0.5, 'rgba(56, 189, 248, 0.25)');
        grad.addColorStop(1, 'rgba(56, 189, 248, 0)');
        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(p3.x, p3.y);
        ctx.lineTo(p4.x, p4.y);
        ctx.stroke();
      }
    }

    // Holographic Pedestal Ring
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.4)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const segments = 32;
    let first = true;
    for (let j = 0; j <= segments; j++) {
      const angle = (j / segments) * Math.PI * 2;
      const rx = Math.cos(angle) * 160;
      const rz = Math.sin(angle) * 160;
      const p = this.project(rx, yPos, rz);
      if (p) {
        if (first) { ctx.moveTo(p.x, p.y); first = false; }
        else { ctx.lineTo(p.x, p.y); }
      }
    }
    ctx.stroke();
    ctx.restore();
  }

  drawParticles() {
    const ctx = this.ctx;
    ctx.save();
    for (const p of this.particles) {
      p.y -= p.speed;
      if (p.y < -200) p.y = 200;

      const proj = this.project(p.x, p.y, p.z);
      if (proj && proj.scale > 0) {
        ctx.fillStyle = this.glowColor;
        ctx.globalAlpha = p.alpha * Math.min(1, proj.scale * 1.5);
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, p.size * proj.scale, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.restore();
  }

  draw3DPictureCard() {
    if (!this.image) return;

    const ctx = this.ctx;
    let cardW = 220;
    let cardH = cardW / this.imageAspect;
    if (cardH > 260) {
      cardH = 260;
      cardW = cardH * this.imageAspect;
    }

    const hw = cardW / 2;
    const hh = cardH / 2;

    // Corner vertices in local 3D object space
    // [TL, TR, BR, BL]
    const corners = [
      { x: -hw, y: -hh, z: 0 },
      { x: hw, y: -hh, z: 0 },
      { x: hw, y: hh, z: 0 },
      { x: -hw, y: hh, z: 0 }
    ];

    const p = corners.map(c => this.project(c.x, c.y, c.z));
    if (p.some(pt => !pt)) return;

    ctx.save();

    // 1. Holographic Glow Aura behind the card
    ctx.shadowColor = this.glowColor;
    ctx.shadowBlur = state.isScanning ? 35 : 20;

    // 2. 3D Card Backing / Bevel Frame
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.strokeStyle = this.glowColor;
    ctx.lineWidth = 2.5;

    ctx.beginPath();
    ctx.moveTo(p[0].x, p[0].y);
    ctx.lineTo(p[1].x, p[1].y);
    ctx.lineTo(p[2].x, p[2].y);
    ctx.lineTo(p[3].x, p[3].y);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 3. Texture Mapping via Affine Quad Split
    // Split into 2 triangles (0-1-2 and 0-2-3) to map image with perspective approximation
    this.drawTexturedTriangle(
      this.image,
      p[0].x, p[0].y, p[1].x, p[1].y, p[2].x, p[2].y,
      0, 0, this.image.width, 0, this.image.width, this.image.height
    );
    this.drawTexturedTriangle(
      this.image,
      p[0].x, p[0].y, p[2].x, p[2].y, p[3].x, p[3].y,
      0, 0, this.image.width, this.image.height, 0, this.image.height
    );

    // 4. Holographic Scan Laser Stripe across the 3D card
    if (state.isScanning) {
      this.scanProgress = (this.scanProgress + 0.015) % 1.0;
      const scanY = -hh + (cardH * this.scanProgress);
      const scanP1 = this.project(-hw, scanY, 2);
      const scanP2 = this.project(hw, scanY, 2);

      if (scanP1 && scanP2) {
        ctx.strokeStyle = '#00f2fe';
        ctx.lineWidth = 4;
        ctx.shadowColor = '#00f2fe';
        ctx.shadowBlur = 20;
        ctx.beginPath();
        ctx.moveTo(scanP1.x, scanP1.y);
        ctx.lineTo(scanP2.x, scanP2.y);
        ctx.stroke();

        // Scan reflection highlight
        ctx.fillStyle = 'rgba(0, 242, 254, 0.15)';
        ctx.beginPath();
        ctx.moveTo(p[0].x, p[0].y);
        ctx.lineTo(p[1].x, p[1].y);
        ctx.lineTo(scanP2.x, scanP2.y);
        ctx.lineTo(scanP1.x, scanP1.y);
        ctx.closePath();
        ctx.fill();
      }
    }

    ctx.restore();
  }

  drawTexturedTriangle(img, x0, y0, x1, y1, x2, y2, u0, v0, u1, v1, u2, v2) {
    const ctx = this.ctx;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.closePath();
    ctx.clip();

    // Compute affine transform matrix
    const delta = u0 * (v1 - v2) - v0 * (u1 - u2) + (u1 * v2 - u2 * v1);
    if (Math.abs(delta) < 0.0001) {
      ctx.restore();
      return;
    }

    const a = (x0 * (v1 - v2) - v0 * (x1 - x2) + (x1 * v2 - x2 * v1)) / delta;
    const b = (u0 * (x1 - x2) - x0 * (u1 - u2) + (u1 * x2 - u2 * x1)) / delta;
    const c = (y0 * (v1 - v2) - v0 * (y1 - y2) + (y1 * v2 - y2 * v1)) / delta;
    const d = (u0 * (y1 - y2) - y0 * (u1 - u2) + (u1 * y2 - u2 * y1)) / delta;
    const e = (x0 * (u1 * v2 - u2 * v1) - u0 * (x1 * v2 - x2 * v1) + v0 * (x1 * u2 - x2 * u1)) / delta;
    const f = (y0 * (u1 * v2 - u2 * v1) - u0 * (y1 * v2 - y2 * v1) + v0 * (y1 * u2 - y2 * u1)) / delta;

    ctx.transform(a, c, b, d, e, f);
    ctx.drawImage(img, 0, 0);
    ctx.restore();
  }

  setAura(verdict) {
    if (verdict === 'REAL') {
      this.glowColor = '#00f59b';
    } else if (verdict === 'REEL') {
      this.glowColor = '#ff2a6d';
    } else {
      this.glowColor = '#f59e0b';
    }
  }

  animate() {
    // Smooth camera interpolation
    this.rotX += (this.targetRotX - this.rotX) * 0.08;
    this.rotY += (this.targetRotY - this.rotY) * 0.08;

    // HUD angles update
    const degX = Math.round((this.rotX * 180) / Math.PI);
    const degY = Math.round((this.rotY * 180) / Math.PI);
    elements.hudAngle.textContent = `${degX}° / ${degY}°`;

    // FPS calculation
    const now = performance.now();
    this.frameCount++;
    if (now - this.lastTime >= 1000) {
      this.currentFps = Math.round((this.frameCount * 1000) / (now - this.lastTime));
      elements.hudFps.textContent = this.currentFps;
      this.frameCount = 0;
      this.lastTime = now;
    }

    // Clear Canvas
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Render 3D Scene
    this.drawGrid();
    this.drawParticles();
    this.draw3DPictureCard();

    requestAnimationFrame(() => this.animate());
  }
}

// Instantiate 3D Stage
let stage = null;
window.addEventListener('DOMContentLoaded', () => {
  stage = new Holographic3DStage(elements.canvas);
  initApp();
});

/* =====================================================================
   2. APPLICATION LOGIC & API INTEGRATION
   ===================================================================== */
function initApp() {
  bindUIEvents();
  checkBrainHealth();
}

function bindUIEvents() {
  // File Dropzone
  elements.dropzone.addEventListener('click', () => elements.fileInput.click());
  elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      loadFile(e.target.files[0]);
    }
  });

  ['dragenter', 'dragover'].forEach(name => {
    elements.dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      elements.dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    elements.dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      elements.dropzone.classList.remove('dragover');
    });
  });

  elements.dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      loadFile(e.dataTransfer.files[0]);
    }
  });

  // 1-Click Sample Test Buttons
  elements.sampleRealBtn.addEventListener('click', () => loadSample('real'));
  elements.sampleAiBtn.addEventListener('click', () => loadSample('ai'));

  // Reset Camera View
  elements.resetCamBtn.addEventListener('click', () => stage.resetCamera());

  // Analyze Action
  elements.analyzeBtn.addEventListener('click', runAnalysis);

  // Settings Modal
  elements.settingsBtn.addEventListener('click', () => {
    elements.apiBaseInput.value = state.apiBase;
    elements.ollamaUrlInput.value = state.ollamaUrl;
    elements.modelNameInput.value = state.modelName;
    elements.settingsModal.classList.remove('hidden');
  });

  elements.closeSettingsBtn.addEventListener('click', () => {
    elements.settingsModal.classList.add('hidden');
  });

  elements.saveSettingsBtn.addEventListener('click', () => {
    state.apiBase = elements.apiBaseInput.value.trim().replace(/\/$/, '');
    state.ollamaUrl = elements.ollamaUrlInput.value.trim() || 'http://localhost:11434';
    state.modelName = elements.modelNameInput.value.trim() || 'qwen2.5-coder:3b';
    localStorage.setItem('realorrell_api_base', state.apiBase);
    localStorage.setItem('realorrell_ollama_url', state.ollamaUrl);
    localStorage.setItem('realorrell_model_name', state.modelName);
    elements.settingsModal.classList.add('hidden');
    checkBrainHealth();
  });

  // Visualizer Tabs
  document.querySelectorAll('.viz-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.viz-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.viz-view').forEach(v => v.classList.remove('active'));
      
      tab.classList.add('active');
      const targetId = tab.dataset.tab === 'ela' ? 'viewEla' : tab.dataset.tab === 'fft' ? 'viewFft' : 'viewOrig';
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Raw Dossier Toggle
  elements.toggleDossierBtn.addEventListener('click', () => {
    elements.rawDossierBox.classList.toggle('hidden');
    elements.toggleDossierBtn.textContent = elements.rawDossierBox.classList.contains('hidden') 
      ? 'View Raw Dossier Fed to Qwen' 
      : 'Hide Raw Dossier';
  });
}

async function checkBrainHealth() {
  elements.brainStatusPill.className = 'status-pill status-checking';
  elements.brainStatusText.textContent = 'Probing AI Brain...';

  try {
    const url = `${state.apiBase}/api/health?ollama_url=${encodeURIComponent(state.ollamaUrl)}&model_name=${encodeURIComponent(state.modelName)}`;
    const res = await fetch(url);
    const data = await res.json();
    
    if (data.brain && data.brain.online) {
      state.brainOnline = true;
      elements.brainStatusPill.className = 'status-pill status-online';
      elements.brainStatusText.textContent = `Qwen Brain Active (${state.modelName})`;
    } else {
      state.brainOnline = false;
      elements.brainStatusPill.className = 'status-pill status-offline';
      elements.brainStatusText.textContent = 'Brain Standby (Forensics Active)';
    }
  } catch (err) {
    state.brainOnline = false;
    elements.brainStatusPill.className = 'status-pill status-offline';
    elements.brainStatusText.textContent = 'Backend Offline';
  }
}

function loadFile(file) {
  state.currentFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      stage.setImage(img);
      elements.analyzeBtn.disabled = false;
      elements.analyzeBtnText.textContent = `Analyze "${file.name.substring(0, 20)}"`;
      elements.origImg.src = e.target.result;
      resetPipeline();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function loadSample(type) {
  try {
    elements.analyzeBtnText.textContent = `Loading ${type.toUpperCase()} sample...`;
    const res = await fetch(`${state.apiBase}/api/sample/${type}`);
    if (!res.ok) throw new Error('Sample not found on server');
    
    const blob = await res.blob();
    const filename = type === 'real' ? 'sample_real.jpg' : 'sample_ai.png';
    const file = new File([blob], filename, { type: blob.type });
    loadFile(file);
  } catch (err) {
    alert(`Could not load sample: ${err.message}`);
  }
}

function resetPipeline() {
  for (let i = 1; i <= 5; i++) {
    const step = document.getElementById(`step${i}`);
    step.className = 'pipeline-item';
    step.querySelector('.step-status').textContent = 'IDLE';
  }
  elements.resultsSection.classList.add('hidden');
  stage.glowColor = '#00f2fe';
}

async function runAnalysis() {
  if (!state.currentFile) return;

  state.isScanning = true;
  elements.hudStatus.textContent = 'SCANNING';
  elements.laserScanner.classList.add('scanning');
  elements.analyzeBtn.disabled = true;
  elements.analyzeBtnText.textContent = 'Extracting Forensics & Reasoning...';

  // Animate pipeline stages
  await animateStep(1, 'EXTRACTING', 350);
  await animateStep(2, 'COMPUTING', 400);
  await animateStep(3, 'TRANSFORMING', 450);
  await animateStep(4, 'MEASURING', 400);
  await animateStep(5, 'SYNTHESIZING', 500);

  const formData = new FormData();
  formData.append('file', state.currentFile);
  formData.append('ollama_url', state.ollamaUrl);
  formData.append('model_name', state.modelName);

  try {
    const res = await fetch(`${state.apiBase}/api/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Analysis failed');
    }

    const data = await res.json();
    displayResults(data);
  } catch (err) {
    alert(`Analysis Error: ${err.message}`);
  } finally {
    state.isScanning = false;
    elements.hudStatus.textContent = 'COMPLETE';
    elements.laserScanner.classList.remove('scanning');
    elements.analyzeBtn.disabled = false;
    elements.analyzeBtnText.textContent = 'Re-Analyze Image';
    for (let i = 1; i <= 5; i++) {
      const step = document.getElementById(`step${i}`);
      step.className = 'pipeline-item completed';
      step.querySelector('.step-status').textContent = 'DONE';
    }
  }
}

function animateStep(stepNum, statusText, delay) {
  return new Promise(resolve => {
    const step = document.getElementById(`step${stepNum}`);
    step.className = 'pipeline-item active';
    step.querySelector('.step-status').textContent = statusText;
    setTimeout(() => {
      step.className = 'pipeline-item completed';
      step.querySelector('.step-status').textContent = 'DONE';
      resolve();
    }, delay);
  });
}

function displayResults(data) {
  state.lastVerdict = data.verdict;
  stage.setAura(data.verdict);

  // Verdict Card
  elements.verdictCard.className = `card verdict-card verdict-${data.verdict.toLowerCase()}`;
  elements.verdictMainBadge.textContent = data.verdict === 'REAL' ? 'ORIGINAL PHOTO' : data.verdict === 'REEL' ? 'AI SYNTHETIC' : 'SUSPICIOUS / HYBRID';
  elements.verdictSummaryText.textContent = data.summary;

  // Confidence Gauge (Circumference 314.15)
  const conf = Math.max(10, Math.min(100, data.confidence));
  const offset = 314.15 - (314.15 * (conf / 100));
  elements.gaugeBar.style.strokeDashoffset = offset;
  elements.confidenceValue.textContent = `${conf}%`;

  // Brain Attribution
  elements.brainAttributionText.textContent = `${data.brain_info.source} ${data.brain_info.active ? '(Neural Brain Active)' : '(Forensics Rule Fallback)'}`;

  // Visualizers
  elements.elaImg.src = data.visualizations.ela_preview;
  elements.fftImg.src = data.visualizations.fft_preview;

  // Metrics Scorecard
  const qm = data.quantitative_metrics;
  elements.mCamera.textContent = qm.has_camera_hardware ? qm.camera_model : 'None Detected';
  elements.mEla.textContent = qm.ela_mean_error;
  elements.mFftSpike.textContent = `${qm.fft_grid_spike_prominence} ${qm.has_periodic_grid_artifacts ? '⚠' : '✓'}`;
  elements.mNoise.textContent = qm.sensor_noise_mean;
  elements.mSharpness.textContent = Math.round(qm.laplacian_variance);
  elements.mSaturation.textContent = `${Math.round(qm.mean_saturation)}/255`;

  // Evidence list
  elements.evidenceList.innerHTML = '';
  (data.key_evidence || []).forEach(ev => {
    const li = document.createElement('li');
    li.textContent = ev;
    elements.evidenceList.appendChild(li);
  });

  // Reasoning Breakdown
  const fb = data.forensic_breakdown || {};
  elements.rMeta.textContent = fb.metadata_provenance || 'Metadata analyzed.';
  elements.rEla.textContent = fb.compression_analysis || 'ELA evaluated.';
  elements.rFft.textContent = fb.frequency_spectrum || '2D FFT spectrum processed.';
  elements.rNoise.textContent = fb.noise_texture || 'Texture dynamics measured.';
  elements.recommendationText.textContent = data.recommendation || 'No additional steps needed.';

  // Raw Dossier
  elements.rawDossierPre.textContent = data.semantic_dossier_text;

  // Reveal Results Section with smooth scroll
  elements.resultsSection.classList.remove('hidden');
  elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
