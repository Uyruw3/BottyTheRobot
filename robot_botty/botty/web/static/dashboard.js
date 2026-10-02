/* Botty Prototype - Dashboard JavaScript */

const API_BASE = '';
const EXPRESSIONS = [
  'idle', 'happy', 'sad', 'angry', 'surprised', 'sleepy', 'loving',
  'thinking', 'confused', 'searching', 'drive', 'developer',
  'talking', 'listening', 'waking_up', 'shut_down'
];

const EMOTION_NAMES = {
  'neutral': 'Neutral', 'happy': 'Feliz', 'sad': 'Triste', 'angry': 'Enojado',
  'surprised': 'Sorprendido', 'fearful': 'Asustado', 'disgusted': 'Disgustado',
  'trusting': 'Confiado', 'anticipating': 'Anticipando', 'joyful': 'Alegre',
  'sorrowful': 'Apenado', 'furious': 'Furioso', 'amazed': 'Asombrado',
  'terrified': 'Aterrorizado', 'serene': 'Sereno'
};

class BottyDashboard {
  constructor() {
    this.expressionGrid = document.getElementById('exprGrid');
    this.chatBox = document.getElementById('chatBox');
    this.chatInput = document.getElementById('chatInput');
    this.logBox = document.getElementById('logBox');
    this.statusGrid = document.getElementById('statusGrid');
    this.sensorData = document.getElementById('sensorData');
    this.videoFeed = document.getElementById('videoFeed');
    this.pluginList = document.getElementById('pluginList');
    this.emotionDisplay = document.getElementById('emotionDisplay');
    this.init();
  }

  init() {
    this.buildExpressionButtons();
    this.initEventListeners();
    this.startPolling();
    this.updateClock();
    setInterval(() => this.updateClock(), 1000);
  }

  buildExpressionButtons() {
    if (!this.expressionGrid) return;
    EXPRESSIONS.forEach(expr => {
      const btn = document.createElement('button');
      btn.className = 'exp-btn';
      btn.dataset.expression = expr;
      btn.textContent = expr.replace(/_/g, ' ');
      btn.onclick = () => this.setExpression(expr);
      this.expressionGrid.appendChild(btn);
    });
  }

  initEventListeners() {
    if (this.chatInput) {
      this.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') this.sendChat();
      });
    }
  }

  async apiCall(endpoint, method = 'GET', body = null) {
    const opts = {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : {}
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const r = await fetch(endpoint, opts);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } catch (err) {
      console.error(`API error ${endpoint}:`, err);
      return null;
    }
  }

  setMode(mode) {
    this.apiCall('/api/mode', 'POST', { mode });
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`btn-${mode}`);
    if (btn) btn.classList.add('active');
    this.showToast(`Modo cambiado a: ${mode}`);
  }

  setExpression(expr) {
    this.apiCall('/api/expression', 'POST', { expression: expr });
    document.querySelectorAll('.exp-btn').forEach(b => b.classList.remove('active'));
    const btn = this.expressionGrid.querySelector(`[data-expression="${expr}"]`);
    if (btn) btn.classList.add('active');
  }

  motorCommand(cmd) {
    this.apiCall('/api/motor', 'POST', { command: cmd });
  }

  async sendChat() {
    const msg = this.chatInput.value.trim();
    if (!msg) return;
    this.addChatMessage(msg, 'user');
    this.chatInput.value = '';
    const data = await this.apiCall('/api/chat', 'POST', { message: msg });
    if (data && data.reply) {
      this.addChatMessage(data.reply, 'bot');
    }
  }

  async speakText(text) {
    if (!text) text = this.chatInput.value.trim();
    if (!text) return;
    await this.apiCall('/api/speak', 'POST', { text });
  }

  addChatMessage(text, cls) {
    if (!this.chatBox) return;
    const d = document.createElement('div');
    d.className = `msg ${cls}`;
    d.textContent = text;
    this.chatBox.appendChild(d);
    this.chatBox.scrollTop = this.chatBox.scrollHeight;
  }

  addLogEntry(msg, level = 'info') {
    if (!this.logBox) return;
    const d = document.createElement('div');
    d.className = `entry ${level}`;
    const time = new Date().toLocaleTimeString();
    d.textContent = `[${time}] ${msg}`;
    this.logBox.appendChild(d);
    if (this.logBox.children.length > 100) {
      this.logBox.removeChild(this.logBox.firstChild);
    }
    this.logBox.scrollTop = this.logBox.scrollHeight;
  }

  updateClock() {
    const el = document.getElementById('clock');
    if (el) el.textContent = new Date().toLocaleTimeString();
  }

  async pollStatus() {
    const d = await this.apiCall('/api/status');
    if (!d) return;

    const statusMode = document.getElementById('statusMode');
    if (statusMode) {
      statusMode.textContent = `Modo: ${d.mode}${d.auto_mode ? ' (Auto)' : ''}`;
    }

    const emotionVal = document.getElementById('emotionVal');
    if (emotionVal) emotionVal.textContent = EMOTION_NAMES[d.emotion] || d.emotion || '--';

    const exprVal = document.getElementById('exprVal');
    if (exprVal) exprVal.textContent = d.expression || '--';

    const userVal = document.getElementById('userVal');
    if (userVal) userVal.textContent = d.current_user || '--';

    if (this.statusGrid) {
      const items = [
        ['Auto', d.auto_mode ? 'Sí' : 'No', d.auto_mode ? 'green' : 'gray'],
        ['Developer', d.developer_mode ? 'Sí' : 'No', d.developer_mode ? 'red' : 'gray'],
        ['Cámara', d.camera_ok ? 'Ok' : 'No', d.camera_ok ? 'green' : 'red'],
        ['Mando', d.controller_ok ? 'Conectado' : 'No', d.controller_ok ? 'green' : 'gray'],
        ['Música', d.music_playing ? 'Sí' : 'No', d.music_playing ? 'green' : 'gray'],
        ['Listener', d.listener_active ? 'Activo' : 'Off', d.listener_active ? 'green' : 'red'],
        ['Lockout', d.lockout > 0 ? `${d.lockout}s` : '0', d.lockout > 0 ? 'red' : 'green'],
        ['Modo', d.mode || '--', 'yellow'],
      ];
      this.statusGrid.innerHTML = items.map(([l, v, c]) =>
        `<div class="status-item">
          <span class="stat-label">${l}</span>
          <span class="stat-value"><span class="indicator ${c}"></span>${v}</span>
        </div>`
      ).join('');
    }

    document.querySelectorAll('.mode-btn').forEach(b => {
      b.classList.toggle('active', b.id === `btn-${d.mode}`);
    });
  }

  async pollSensors() {
    const d = await this.apiCall('/api/sensors');
    if (!d || !this.sensorData) return;

    const sonar = d.sonar || {};
    const imu = d.imu || {};

    let html = '';

    if (Object.keys(sonar).length > 0) {
      html += '<div style="font-size:0.8em;color:var(--accent);margin-bottom:6px">Ultrasonido</div>';
      html += Object.entries(sonar).map(([k, v]) =>
        `<div class="status-item">
          <span class="stat-label">${k}</span>
          <span class="stat-value">${v.toFixed(1)} cm</span>
        </div>`
      ).join('');
    }

    if (Object.keys(imu).length > 0) {
      html += '<div style="font-size:0.8em;color:var(--accent);margin-top:8px;margin-bottom:6px">IMU</div>';
      html += Object.entries(imu).map(([k, v]) =>
        `<div class="status-item">
          <span class="stat-label">${k}</span>
          <span class="stat-value">${v}</span>
        </div>`
      ).join('');
    }

    this.sensorData.innerHTML = html || '<div class="label">No hay datos de sensores</div>';
  }

  async pollEmotion() {
    const d = await this.apiCall('/api/emotion');
    if (!d) return;

    const emotionVal = document.getElementById('emotionValDetail');
    if (emotionVal) {
      emotionVal.textContent = EMOTION_NAMES[d.emotion] || d.emotion || '--';
    }

    if (this.emotionDisplay && d.dimensions) {
      const v = d.dimensions.valence || 0.5;
      const a = d.dimensions.arousal || 0.5;
      this.emotionDisplay.innerHTML = `
        <div class="emotion-bar">
          <div class="fill ${v > 0.6 ? 'high' : v > 0.3 ? 'med' : 'low'}" style="width:${v * 100}%"></div>
        </div>
        <span style="font-size:0.75em;color:var(--text-secondary);min-width:50px">Valencia: ${(v * 100).toFixed(0)}%</span>
        <div class="emotion-bar">
          <div class="fill ${a > 0.6 ? 'high' : a > 0.3 ? 'med' : 'low'}" style="width:${a * 100}%"></div>
        </div>
        <span style="font-size:0.75em;color:var(--text-secondary);min-width:50px">Activación: ${(a * 100).toFixed(0)}%</span>
      `;
    }
  }

  async pollPlugins() {
    const d = await this.apiCall('/api/plugins');
    if (!d || !this.pluginList) return;

    const plugins = d.plugins || [];
    if (plugins.length === 0) {
      this.pluginList.innerHTML = '<div class="label">No hay plugins cargados</div>';
      return;
    }

    this.pluginList.innerHTML = plugins.map(p =>
      `<div class="plugin-item">
        <span class="plugin-name">${p.name}</span>
        <span>
          <span class="plugin-status ${p.enabled ? 'loaded' : 'disabled'}">
            ${p.enabled ? '● Activo' : '○ Inactivo'}
          </span>
          <button class="btn small" onclick="dashboard.togglePlugin('${p.name}')">
            ${p.enabled ? 'Desactivar' : 'Activar'}
          </button>
        </span>
      </div>`
    ).join('');
  }

  async togglePlugin(name) {
    await this.apiCall('/api/plugins/toggle', 'POST', { name });
    this.pollPlugins();
  }

  async pollLogs() {
    const d = await this.apiCall('/api/logs');
    if (!d || !d.logs || !this.logBox) return;

    d.logs.forEach(l => {
      const existing = Array.from(this.logBox.children).some(
        child => child.textContent.includes(l.msg)
      );
      if (!existing) {
        const entry = document.createElement('div');
        entry.className = `entry ${l.level || 'info'}`;
        const time = new Date(l.time * 1000).toLocaleTimeString();
        entry.textContent = `[${time}] ${l.msg}`;
        this.logBox.appendChild(entry);
      }
    });

    if (this.logBox.children.length > 200) {
      while (this.logBox.children.length > 150) {
        this.logBox.removeChild(this.logBox.firstChild);
      }
    }
    this.logBox.scrollTop = this.logBox.scrollHeight;
  }

  startPolling() {
    const pollAll = () => {
      this.pollStatus();
      this.pollSensors();
      this.pollEmotion();
      this.pollPlugins();
    };

    pollAll();
    setInterval(() => this.pollStatus(), 2000);
    setInterval(() => this.pollSensors(), 3000);
    setInterval(() => this.pollEmotion(), 2000);
    setInterval(() => this.pollPlugins(), 5000);
    setInterval(() => this.pollLogs(), 2000);
  }

  showToast(msg, duration = 3000) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  toggleTheme() {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    localStorage.setItem('botty-theme', isLight ? 'light' : 'dark');
  }
}

const dashboard = new BottyDashboard();
