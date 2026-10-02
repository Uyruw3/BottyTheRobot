# Botty Prototype v0.1.0 Alpha

Robot autónomo con IA, visión por cámara, reconocimiento facial, voz interactiva,
memoria a largo plazo, sistema de emociones, plugins extensibles y panel web de control.

Esta es la edición de Botty para el robot físico. La edición `botty-desktop/`
lleva el mismo compañero a una aplicación Windows independiente; cada edición
tiene su implementación e instalación propias.

> **Estado:** Alpha — nada de lo que ves es final.
> **Versión:** 0.1.0
> **Plataforma:** Raspberry Pi 5 (robot físico) / Windows (desarrollo y simulación)
> **Idioma:** Español

---

## Características

### 🤖 Sistema Principal
- Bucle principal a 60 FPS con Pygame
- 3 modos de operación: Auto, Manual y Developer
- Micro siempre activo (escucha en segundo plano)
- Interfaz por voz y teclado
- Texto instructivo "W.I.P WORK IN PROGRESS"

### 👁️ Ojos Expresivos (EMO Style)
- Ojos tipo rounded rect con pupil tracking
- 17+ expresiones faciales (feliz, triste, enojado, sorprendido, amoroso, etc.)
- Parpadeo asimétrico estilo EMO real
- Modo arco (happy arch) para sonrisa
- Pupila sigue el cursor del mouse o la cara detectada
- Reacciona al click/touch con expresiones y voz
- Scan line animada tipo display LED
- Efectos: corazón (modo love), ZZZ (modo sleepy)
- Parpadeo automático cada 3.5s

### 🖥️ Manos Digitales (Desktop Hands)
- Juega con ventanas del escritorio cuando está idle
- Menea, empuja, minimiza y restaura ventanas
- No toca ventanas críticas ni la propia de Botty
- Los ojos miran hacia la ventana que está moviendo

### 🧠 Sistema de Emociones
- Modelo bidimensional: Valencia (+/-) y Activación (+/-)
- 15 estados emocionales (feliz, triste, enojado, sorprendido, amoroso, etc.)
- Decaimiento natural al neutro
- Personalidad configurable (alegre, gruñón, enérgico, tranquilo, curioso)
- Eventos del mundo real afectan el estado de ánimo
- Analiza conversaciones para detectar cumplidos e insultos
- Selección automática de expresión visual según emoción dominante

### 🎙️ Voz Interactiva
- Reconocimiento de voz con SpeechRecognition (Google API)
- Síntesis de voz con pyttsx3 o gTTS
- Diálogos predefinidos para respuestas rápidas
- 8+ categorías de respuestas (saludos, despedidas, chistes, etc.)
- Reacciones al tacto (click en pantalla)
- Frases de aburrimiento cuando está idle
- Anuncio de modo al activar Developer Mode

### 🌐 Dashboard Web (Flask)
- Puerto 5000, interfaz responsive
- Live feed de cámara (MJPEG)
- Control de modos (Auto/Manual/Developer)
- Grid de botones para expresiones
- Chat interactivo con la IA
- Control de motores (WASD-style)
- Estado en tiempo real (emociones, sensores)
- Logs en vivo
- APIs REST para control remoto

### 🧩 Sistema de Plugins
- Descubrimiento automático desde ~/.botty/plugins/
- 26 tipos de eventos (STARTUP, SHUTDOWN, FACE_DETECTED, VOICE_COMMAND, etc.)
- Prioridades de ejecución
- Plugins incluidos:
  - **Greeter**: Saluda automáticamente a caras conocidas
  - **MusicAnnouncer**: Anuncia cambios de canción
  - **WeatherReporter**: Responde preguntas sobre el clima
  - **Timer**: Temporizador con alarma por voz
  - **Screenshot**: Captura de pantalla
  - **VolumeControl**: Control de volumen del sistema
  - **WallpaperChanger**: Cambia el fondo de pantalla
  - **Pomodoro**: Técnica Pomodoro para productividad
  - **Translator**: Traduce texto entre idiomas
  - **Calculator**: Evalúa expresiones matemáticas
  - **Dice**: Lanza dados virtuales (d4 a d100)
  - **Quote**: Citas inspiradoras y frases célebres
  - **Compliment**: Da cumplidos aleatorios

### 💾 Memoria
- **Memoria facial**: Reconoce caras conocidas y recuerda interacciones
- **Memoria vectorial**: TF-IDF + cosine similarity para búsqueda semántica
- Almacena hasta 1000 conversaciones en JSON
- Tags y metadatos por entrada
- Olvido automático de recuerdos viejos

### 📦 Conocimiento
- Base de personalidad con gustos, disgustos, miedos y sueños
- Datos curiosos sobre robótica e IA
- Chistes y humor robot
- Sistema de diálogo con 15 categorías de respuestas
- Comandos de escritorio reconocibles por voz

### 🔬 RL (Aprendizaje por Refuerzo)
- Entorno Gymnasium personalizado con obstáculos
- Curriculum learning por etapas de dificultad
- Búsqueda aleatoria de hiperparámetros
- Evaluación con estadísticas detalladas
- Modelos PPO con Stable Baselines3

### 🛡️ Modo Desarrollador
- Activado solo por el dueño reconocido facialmente
- Obediencia total a comandos del dueño
- Bloquea keywords peligrosas (quema, destruye, etc.)
- Lockout de 10s en comando peligroso
- Auto-desactivación si el dueño sale del frame

---

## Requisitos

### Windows (Escritorio)
- Python 3.10+
- Pygame, OpenCV, pyttsx3, gTTS, openai, duckduckgo_search, yt-dlp
- Opcional: Flask (dashboard web), pygetwindow (manos digitales), PyAudio (micrófono)

### Raspberry Pi 5 (Robot físico)
- Python 3.10+
- RPi.GPIO, luma.oled, HC-SR04, L298N
- Cámara USB o CSI
- Pantalla TFT/OLED 480x320
- Altavoz y micrófono USB

---

## Instalación

```bash
# Clonar e instalar
git clone https://github.com/tu-usuario/botty-prototype.git
cd botty-prototype
pip install -e .

# Con extras
pip install -e ".[web]"     # Dashboard Flask
pip install -e ".[rl]"      # Aprendizaje por refuerzo
pip install -e ".[oled]"    # Pantalla OLED
pip install -e ".[all]"     # Todo

# Instalar extras manuales (Windows)
pip install pygetwindow     # Manos digitales
pip install SpeechRecognition PyAudio  # Voz
```

---

## Uso

```bash
# Iniciar Botty
python -m botty

# Dashboard web
botty-web

# Entrenar RL
botty-train-rl --train --stages 3 --steps 50000

# Buscar hiperparámetros RL
botty-train-rl --search --trials 10

# Evaluar modelo RL
botty-train-rl --evaluate ruta/al/modelo.zip
```

### Controles

| Tecla | Acción |
|-------|--------|
| ENTER | Modo escritura → mensaje a la IA |
| ESPACIO | Escucha por micrófono |
| ESC | Sale del programa o cancela escritura |
| Click | Los ojos reaccionan y Botty habla |
| Mouse | Los ojos siguen el cursor |

### Comandos de voz

| Comando | Acción |
|---------|--------|
| "modo auto" | Activa modo autónomo |
| "modo manual" | Activa modo mando |
| "developer mode" | Activa modo desarrollador (solo dueño) |
| "busca [consulta]" | Busca en internet |
| "pon música de [canción]" | Reproduce música |
| "adelante / atrás / gira" | Control de movimiento (modo dev) |
| "detente / para" | Detiene motores |
| "empuja" | Activa la pala delantera |

---

## Estructura del proyecto

```
botty/
├── __init__.py          # Paquete principal
├── __main__.py          # Entry point
├── main.py              # Bucle principal (~800 líneas)
├── config.py            # Configuración
├── ai/
│   └── brain.py         # IA con OpenAI/Ollama + tool calling
├── audio/
│   ├── stt.py           # Speech-to-Text
│   └── tts.py           # Text-to-Speech
├── data/
│   ├── dialogues.py     # Diálogos y comandos
│   └── animations_extended.py  # Animaciones extra
├── display/
│   ├── oled.py          # Control OLED SSD1306
│   └── eye_renderer_oled.py  # Ojos para OLED
├── emotion/
│   └── emotion.py       # Sistema de emociones
├── eyes/
│   ├── animations.py    # Estados de expresión
│   └── renderer.py      # Renderizado EMO-style
├── knowledge/
│   ├── personality.py   # Personalidad, datos, humor
│   └── responses.py     # Respuestas de voz
├── memory/
│   ├── face_memory.py   # Memoria facial
│   └── vector_memory.py # Memoria vectorial
├── movement/
│   └── motors.py        # Control de motores L298N
├── plugins/
│   ├── event_types.py   # Tipos de eventos
│   ├── plugin_manager.py # Gestor de plugins
│   └── examples/        # 13 plugins de ejemplo
├── rl/
│   ├── obstacle_avoidance.py  # RL original
│   └── trainer.py       # Trainer mejorado
├── sensors/
│   └── ultrasonic.py    # Sensores HC-SR04
├── tools/
│   ├── controller.py    # Mando Xbox/PS4
│   ├── desktop_hands.py # Manos digitales
│   ├── music.py         # Reproductor de música
│   └── web_search.py    # Búsqueda DuckDuckGo
├── vision/
│   ├── camera.py        # Cámara OpenCV
│   ├── face_recognition.py  # Reconocimiento facial
│   └── object_detection.py  # Detección de objetos
└── web/
    ├── dashboard.py     # Servidor Flask
    ├── templates/
    │   └── dashboard.html  # Interfaz web
    └── static/
tests/
├── test_emotion.py      # Tests de emociones
├── test_eyes.py          # Tests de ojos
├── test_memory.py        # Tests de memoria
├── test_plugins.py       # Tests de plugins
├── test_config.py        # Tests de configuración
├── test_brain.py         # Tests de IA
├── test_voice.py         # Tests de voz
├── test_motors.py        # Tests de motores
├── test_sensors.py       # Tests de sensores
├── test_main.py          # Tests del bucle principal
├── test_vision.py        # Tests de visión
├── test_desktop_hands.py # Tests de manos
├── test_web.py           # Tests de web
scripts/
├── install.sh            # Instalador para Pi
├── botty.service          # systemd autostart
├── flash_botty.py        # Herramienta USB flash
├── flash_botty.spec      # PyInstaller spec
├── build_exe.bat         # Compilar .exe
└── setup_usb_gadget.sh   # USB gadget mode
```

---

## Licencia

MIT — Código abierto para la comunidad robótica.

---

## Créditos

- Inspirado en Living.AI EMO y robots con personalidad
- Construido con Python, Pygame, OpenCV, y mucho cariño
- Creado por un humano con más café que sentido común

---

*"La vida es mejor sobre ruedas."* — Botty
