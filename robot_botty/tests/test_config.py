"""
Tests for configuration module.
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"


def test_config_import():
    from botty.config import Config
    assert Config.DISPLAY_WIDTH > 0
    assert Config.DISPLAY_HEIGHT > 0
    assert Config.EYE_FPS > 0
    print("  OK test_config_import")


def test_config_display():
    from botty.config import Config
    assert isinstance(Config.DISPLAY_FULLSCREEN, bool)
    assert isinstance(Config.DISPLAY_WIDTH, int)
    assert isinstance(Config.DISPLAY_HEIGHT, int)
    print("  OK test_config_display")


def test_config_ai():
    from botty.config import Config
    assert Config.AI_PROVIDER in ("ollama", "openai")
    assert Config.OLLAMA_MODEL != ""
    assert Config.AI_SYSTEM_PROMPT != ""
    print("  OK test_config_ai")


def test_config_audio():
    from botty.config import Config
    assert Config.STT_LANGUAGE == "es-ES"
    assert Config.TTS_LANGUAGE == "es"
    assert Config.TTS_SPEED > 0
    print("  OK test_config_audio")


def test_config_motors():
    from botty.config import Config
    assert isinstance(Config.MOTOR_ENABLED, bool)
    assert Config.MOTOR_MAX_SPEED > 0
    assert Config.MOTOR_MAX_SPEED <= 100
    print("  OK test_config_motors")


def test_config_sensors():
    from botty.config import Config
    assert Config.SONAR_OBSTACLE_THRESHOLD > 0
    assert Config.SONAR_FLEE_THRESHOLD > 0
    assert Config.SONAR_FLEE_THRESHOLD < Config.SONAR_OBSTACLE_THRESHOLD
    print("  OK test_config_sensors")


def test_config_developer():
    from botty.config import Config
    assert Config.DEVELOPER_OWNER_NAME != ""
    assert Config.DEVELOPER_LOCK_OUT > 0
    assert len(Config.DEVELOPER_DANGEROUS_KEYWORDS) > 0
    print("  OK test_config_developer")


def test_config_face():
    from botty.config import Config
    assert Config.KNOWN_FACES_DIR != ""
    assert Config.FACE_DETECTION_MODEL in ("hog", "cnn")
    assert 0 < Config.RECOGNITION_TOLERANCE <= 1.0
    print("  OK test_config_face")


def test_config_eye():
    from botty.config import Config
    assert Config.EYE_FPS >= 30
    assert Config.EYE_BLINK_INTERVAL > 0
    assert Config.EYE_BLINK_DURATION > 0
    print("  OK test_config_eye")


def test_config_env_vars(monkeypatch):
    import importlib
    import botty.config
    monkeypatch.setenv("BOTTY_OWNER", "test_user")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    try:
        C2 = importlib.reload(botty.config).Config
        assert C2.DEVELOPER_OWNER_NAME == "test_user"
    finally:
        monkeypatch.undo()
        importlib.reload(botty.config)
    print("  OK test_config_env_vars")


if __name__ == "__main__":
    test_config_import()
    test_config_display()
    test_config_ai()
    test_config_audio()
    test_config_motors()
    test_config_sensors()
    test_config_developer()
    test_config_face()
    test_config_eye()
    test_config_env_vars()
    print("\nTodos los tests de config pasados!")
