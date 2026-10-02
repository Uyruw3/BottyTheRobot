#!/bin/bash
# ── Botty Robot — Instalador para Raspberry Pi ──
#
# Modos:
#   bash scripts/install.sh          Instalacion completa (primera vez)
#   bash scripts/install.sh --update Solo actualiza codigo y reinicia servicio
#
set -e

UPDATE_MODE=false
if [ "$1" == "--update" ] || [ "$1" == "-u" ]; then
    UPDATE_MODE=true
fi

echo "=============================="
echo "  Botty Robot — Instalador"
if $UPDATE_MODE; then
    echo "  (Modo actualizacion rapida)"
fi
echo "=============================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Dependencias del sistema (solo primera vez) ──
if ! $UPDATE_MODE; then
    echo ""
    echo "[1/5] Instalando dependencias del sistema..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        python3-pip python3-venv python3-full \
        python3-opencv \
        libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
        libportaudio2 libportaudiocpp0 portaudio19-dev \
        espeak espeak-data libespeak1 \
        alsa-utils pulseaudio \
        ffmpeg \
        python3-smbus i2c-tools \
        git

    # ── 2. Crear directorios ──
    echo ""
    echo "[2/5] Creando directorios..."
    mkdir -p ~/.botty/known_faces
    mkdir -p ~/.botty/logs

    # ── 3. Entorno virtual ──
    echo ""
    echo "[3/5] Creando entorno virtual..."
    python3 -m venv ~/.botty/venv
else
    echo ""
    echo "[1/2] Modo actualizacion — saltando dependencias del sistema"
fi

# ── Activar venv (o crearlo si no existe) ──
if [ ! -f ~/.botty/venv/bin/activate ]; then
    echo "  -> Creando entorno virtual (no existia)..."
    python3 -m venv ~/.botty/venv
fi
source ~/.botty/venv/bin/activate

# ── Instalar/actualizar paquete Python ──
echo ""
echo "Instalando paquete Python..."
pip install --upgrade pip -q

if $UPDATE_MODE; then
    # Modo update: solo instala dependencias faltantes
    echo "  -> Verificando dependencias..."
    pip install -e . --no-deps -q
    pip install RPi.GPIO -q
    # Revisar si faltan dependencias
    pip install -e . -q || true
else
    pip install -e .
    pip install RPi.GPIO
fi

# ── 4. Configurar autostart (solo primera vez) ──
if ! $UPDATE_MODE; then
    echo ""
    echo "[4/5] Configurando autostart..."

    # Crear .env por defecto si no existe
    if [ ! -f ~/.botty/.env ]; then
        cat > ~/.botty/.env << 'EOF'
# Botty Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
TTS_ENGINE=pyttsx3
EOF
        echo "  -> Creado ~/.botty/.env (EDITALO con tu API key)"
    fi

    # Copiar e instalar servicio systemd
    sudo cp scripts/botty.service /etc/systemd/system/botty.service
    sudo systemctl daemon-reload
    sudo systemctl enable botty.service

    # ── 5. Configurar permisos ──
    echo ""
    echo "[5/5] Configurando permisos..."
    sudo raspi-config nonint do_i2c 0 2>/dev/null || true
    sudo usermod -a -G gpio,i2c,spi,video,audio "$USER"
else
    echo ""
    echo "[2/2] Reiniciando servicio..."
    sudo cp scripts/botty.service /etc/systemd/system/botty.service
    sudo systemctl daemon-reload
    sudo systemctl restart botty.service 2>/dev/null || true
fi

echo ""
echo "=============================="
if $UPDATE_MODE; then
    echo "  Actualizacion completada!"
    echo "  Botty reiniciado."
else
    echo "  Instalacion completada!"
    echo "  REINICIA para aplicar: sudo reboot"
fi
echo "=============================="
echo ""
echo "  Probar ahora:"
echo "    source ~/.botty/venv/bin/activate"
echo "    botty"
echo ""
