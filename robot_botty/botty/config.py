import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
load_dotenv(dotenv_path=Path.home() / ".botty" / ".env")


class Config:
    VERSION = "0.1.0"

    # ── Display ──
    DISPLAY_WIDTH = 480
    DISPLAY_HEIGHT = 320
    DISPLAY_FULLSCREEN = os.getenv("BOTTY_FULLSCREEN", "false").lower() == "true"
    FULLSCREEN = DISPLAY_FULLSCREEN
    DISPLAY_DRIVER = "pygame"
    FB_DEVICE = "/dev/fb1"
    FPS = 60
    SHOW_WIP = os.getenv("BOTTY_SHOW_WIP", "true").lower() == "true"
    WIP_TEXT = "W.I.P WORK IN PROGRESS"

    # ── OLED (SSD1306 128x64) ──
    OLED_ENABLED = os.getenv("BOTTY_OLED", "false").lower() == "true"
    OLED_I2C_PORT = 1
    OLED_I2C_ADDR = 0x3C
    OLED_WIDTH = 128
    OLED_HEIGHT = 64

    # ── Camera ──
    CAMERA_ID = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FRAMERATE = 30
    CAMERA_BACKEND = "opencv"
    CAMERA_AUTO_START = False

    # ── AI ──
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    AI_MODEL = os.getenv("AI_MODEL", os.getenv("OLLAMA_MODEL", "qwen2.5:3b"))
    OPENAI_MAX_TOKENS = 512
    OPENAI_TEMPERATURE = 0.7
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_HOST = OLLAMA_URL
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    AI_SYSTEM_PROMPT = (
        "Eres Botty, un robot autonomo con ruedas con personalidad curiosa y servicial. "
        "Tienes sensores ultrasonicos, camara, pantalla OLED para expresiones, "
        "y una pala delantera para empujar objetos. "
        "Puedes reconocer caras, esquivar obstaculos, buscar en internet, "
        "reproducir musica y recordar a las personas. "
        "Respondes en espanol de forma breve y natural, como un amigo."
    )
    AI_MAX_HISTORY = 20
    AI_ENABLED = True

    # ── Audio ──
    STT_ENGINE = os.getenv("STT_ENGINE", "google")
    STT_LANGUAGE = "es-ES"
    TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")
    TTS_LANGUAGE = "es"
    TTS_SPEED = 160
    MIC_DEVICE_INDEX = None
    WAKE_WORD = "botty"
    VOICE_ACTIVATION_THRESHOLD = 300
    VOICE_TIMEOUT = 5.0
    VOICE_PHRASE_LIMIT = 8.0
    WHISPER_MODEL = "base"
    MIC_AUTO_START = True

    # ── Face Recognition ──
    FACE_RECOGNITION_ENABLED = True
    KNOWN_FACES_DIR = os.getenv(
        "BOTTY_FACES_DIR", str(Path.home() / ".botty" / "known_faces")
    )
    FACE_DETECTION_MODEL = "hog"
    RECOGNITION_TOLERANCE = 0.6

    # ── Developer Mode ──
    DEVELOPER_OWNER_NAME = os.getenv("BOTTY_OWNER", "dueno").lower()
    DEVELOPER_PHRASE = "developer mode"
    DEVELOPER_LOCK_OUT = 10
    DEVELOPER_DANGEROUS_KEYWORDS = [
        "salta", "quema", "destruye", "rompe", "golpea",
        "ataca", "dispara", "explota", "mata", "cortar",
        "veneno", "arma", "incendia", "tirar", "piso alto",
        "escalera", "agua", "mojar",
    ]

    # ── Memory ──
    MEMORY_ENABLED = True
    MEMORY_DB_PATH = str(Path.home() / ".botty" / "memory.json")
    MEMORY_MAX_ENTRIES = 1000
    MEMORY_AUTO_SAVE = True
    MEMORY_AUTO_SAVE_INTERVAL = 60

    # ── Motors ──
    MOTOR_ENABLED = False
    MOTOR_LEFT_FORWARD = 17
    MOTOR_LEFT_BACKWARD = 18
    MOTOR_LEFT_ENABLE = 13
    MOTOR_RIGHT_FORWARD = 22
    MOTOR_RIGHT_BACKWARD = 23
    MOTOR_RIGHT_ENABLE = 24
    MOTOR_MAX_SPEED = 70
    MOTOR_PWM_FREQ = 1000
    MOTOR_ACCELERATION = 0.1
    PWM_PIN = 18
    DIR_PINS = [23, 24, 25]

    # ── Ultrasonic sensors (HC-SR04) ──
    SONAR_ENABLED = False
    ULTRASONIC_PINS = {
        "front_trigger": 5,
        "front_echo": 6,
        "left_trigger": 12,
        "left_echo": 16,
        "right_trigger": 20,
        "right_echo": 21,
    }
    SONAR_OBSTACLE_THRESHOLD = 30.0
    SONAR_FLEE_THRESHOLD = 20.0

    # ── Object detection ──
    OBJECT_DETECTION_ENABLED = True
    OBJECT_FLEE_DISTANCE = 1.5
    OBJECT_MIN_AREA = 500

    # ── RL Obstacle Avoidance ──
    RL_ENABLED = False
    RL_MODEL_PATH = str(Path.home() / ".botty" / "models" / "ppo_botty.zip")
    RL_TOTAL_TIMESTEPS = 100000
    RL_LEARNING_RATE = 0.0003
    RL_BUFFER_SIZE = 50000
    RL_BATCH_SIZE = 256
    RL_GAMMA = 0.99

    # ── Front shovel ──
    SHOVEL_ENABLED = False
    SHOVEL_PIN = 26
    SHOVEL_PUSH_DURATION = 2.0

    # ── Controller ──
    CONTROLLER_ENABLED = True
    CONTROLLER_DEADZONE = 0.15
    CONTROLLER_AXIS_LEFT_X = 0
    CONTROLLER_AXIS_LEFT_Y = 1
    CONTROLLER_AXIS_RIGHT_X = 2
    CONTROLLER_AXIS_RIGHT_Y = 3
    CONTROLLER_DRIVE_SPEED = 80

    # ── Eyes ──
    EYE_FPS = 60
    EYE_BLINK_INTERVAL = 4.0
    EYE_BLINK_DURATION = 0.15
    EYE_DEFAULT_COLOR = (70, 130, 220)
    EYE_WIDTH = 80
    EYE_HEIGHT = 100
    EYE_SPACING = 60
    PUPIL_SIZE = 14
    IRIS_COLOR = (70, 130, 180)
    GLOW_INTENSITY = 0.3
    SCANLINE_OPACITY = 0.05
    LOOK_SPEED = 4.0
    IDLE_ROAM_INTERVAL = 1.0
    IDLE_ROAM_RANGE = 0.3

    # ── Web Dashboard ──
    WEB_ENABLED = os.getenv("BOTTY_WEB_ENABLED", "true").lower() == "true"
    WEB_HOST = os.getenv("BOTTY_WEB_HOST", "127.0.0.1")
    WEB_PORT = int(os.getenv("BOTTY_WEB_PORT", "5000"))
    WEB_DEBUG = os.getenv("BOTTY_WEB_DEBUG", "false").lower() == "true"

    # ── Desktop Hands ──
    DESKTOP_HANDS_ENABLED = True
    IDLE_ACTION_INTERVAL_MIN = 6
    IDLE_ACTION_INTERVAL_MAX = 15
    WINDOW_WIGGLE_AMOUNT = 5
    WINDOW_NUDGE_AMOUNT = 20
    WINDOW_BLACKLIST = ["botty", "Program Manager", "Task Manager"]

    # ── Emotion ──
    EMOTION_DECAY_RATE = 0.001
    EMOTION_PERSONALITY = "curious"
    EMOTION_EVENT_COOLDOWN = 0.3

    # ── Plugins ──
    PLUGINS_ENABLED = True
    PLUGINS_DIRECTORY = str(Path.home() / ".botty" / "plugins")
    PLUGINS_AUTO_LOAD = True

    # ── Network ──
    NETWORK_TIMEOUT = 10

    # ── Debug ──
    DEBUG = os.getenv("BOTTY_DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("BOTTY_LOG_LEVEL", "info")
    PROFILE = False
    SHOW_FPS = False
