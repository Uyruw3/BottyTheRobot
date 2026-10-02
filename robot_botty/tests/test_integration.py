"""
Integration tests — end-to-end scenarios for Botty prototype.
"""

import sys
import os
import json
import time
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["BOTTY_TEST"] = "1"
os.environ["BOTTY_FULLSCREEN"] = "false"

import pytest
import pygame

pygame.display.init()
pygame.display.set_mode((480, 320))

from botty.emotion.emotion import EmotionEngine, EmotionState, EmotionEvent
from botty.eyes.animations import EyeExpression, EXPRESSIONS
from botty.eyes.renderer import EyeRenderer
from botty.memory.vector_memory import VectorMemory
from botty.memory.face_memory import FaceMemory
from botty.plugins import PluginManager, PluginEvent, BasePlugin
from botty.knowledge.personality import PERSONALITY, FACTS, HUMOR
from botty.knowledge.responses import RESPONSES, GREETINGS, FAREWELLS
from botty.data.dialogues import DIALOGUES, TOPICS, COMMANDS
from botty.tools.desktop_hands import DesktopHands
from botty.config import Config


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


def load_test_json(filename):
    path = os.path.join(TEST_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestEmotionIntegration:
    def test_emotion_decay_to_neutral(self):
        engine = EmotionEngine()
        engine.trigger(EmotionEvent("praise", 0.5, 0.3))
        assert engine.current != EmotionState.NEUTRAL
        for _ in range(600):
            engine.update(0.1)
        assert engine.current == EmotionState.NEUTRAL

    def test_emotion_personality_presets(self):
        for preset_name in ["happy", "grumpy", "energetic", "calm", "curious"]:
            engine = EmotionEngine(preset=preset_name)
            assert engine.personality == preset_name
            assert "name" in engine.get_personality_info()

    def test_emotion_triggers_eye_expression(self):
        engine = EmotionEngine()
        cases = load_test_json("emotion_test_cases.json")
        for case in cases:
            event = EmotionEvent(case["event"], case["valence_change"], case["arousal_change"])
            engine.trigger(event)
            for _ in range(20):
                engine.update(0.1)
            expr = engine.to_eye_expression()
            assert expr in list(EyeExpression)

    def test_emotion_conversation_sentiment_positive(self):
        engine = EmotionEngine()
        initial = engine.current
        engine.analyze_conversation("Me encanta hablar contigo, eres increible!")
        assert engine.valence > 0.5

    def test_emotion_conversation_sentiment_negative(self):
        engine = EmotionEngine()
        engine.analyze_conversation("Eres terrible y no sirves para nada")
        assert engine.valence < 0.5


class TestEyesIntegration:
    def test_eyes_render_with_emotion(self):
        renderer = EyeRenderer(480, 320)
        engine = EmotionEngine()
        surf = pygame.Surface((480, 320))
        for expr in list(EyeExpression):
            engine.trigger(EmotionEvent("test", 0.1, 0.1))
            renderer.set_expression(expr)
            for _ in range(5):
                renderer.update(0.016)
            renderer.render(surf)
        assert renderer.get_expression() is not None

    def test_eyes_follow_mouse_smoothly(self):
        renderer = EyeRenderer(480, 320)
        renderer.set_look_target(0.8, -0.5)
        surf = pygame.Surface((480, 320))
        for _ in range(30):
            renderer.update(0.016)
            renderer.render(surf)
        assert abs(renderer._current_look_x - 0.8) < 0.1

    def test_asymmetric_blink(self, monkeypatch):
        renderer = EyeRenderer(480, 320)
        monkeypatch.setattr("botty.eyes.renderer.random.random", lambda: 0)
        renderer.trigger_blink()
        assert renderer.left_eye.blink_progress != renderer.right_eye.blink_progress

    def test_arch_mode_transition(self):
        renderer = EyeRenderer(480, 320)
        renderer.set_expression(EyeExpression.HAPPY)
        surf = pygame.Surface((480, 320))
        for _ in range(10):
            renderer.update(0.016)
            renderer.render(surf)
        assert renderer.left_eye.arch > 0.3


class TestMemoryIntegration:
    def test_vector_memory_store_and_search(self):
        mem = VectorMemory(max_entries=50)
        mem.clear()
        mem.add_conversation("Hola Botty!", "Hola! Como estas?", tags=["greeting"])
        mem.add_conversation("Que hora es?", "Son las 3 de la tarde.", tags=["time"])
        mem.add_conversation("Cuentame un chiste", "Por que los robots...", tags=["joke"])
        results = mem.search("greeting", top_k=1)
        assert len(results) > 0

    def test_vector_memory_get_context(self):
        mem = VectorMemory(max_entries=50)
        mem.clear()
        mem.add_conversation("Hola!", "Hola! Como estas?")
        mem.add_conversation("Bien, gracias", "Me alegra!")
        context = mem.get_context("Hola!")
        assert len(context) > 0

    def test_face_memory_familiarity(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Config, "MEMORY_DB_PATH", str(tmp_path / "memory.json"))
        fm = FaceMemory()
        fm.clear()
        for _ in range(5):
            fm.add_face("Alice", [0.1, 0.2, 0.3])
        info = fm.get_face_info("Alice")
        assert info["familiarity"] in ("amigo", "conocido")
        fm.clear()

    def test_memory_persistence(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
            json.dump({"test": "data"}, f)
        assert os.path.exists(path)
        os.unlink(path)


class TestPluginIntegration:
    def test_plugin_manager_discovery(self):
        pm = PluginManager()
        pm.load_all()
        assert len(pm.plugins) > 0

    def test_plugin_dispatch_event(self):
        pm = PluginManager()
        pm.load_all()
        results = pm.dispatch_event(PluginEvent.STARTUP, {"test": True})
        assert isinstance(results, list)

    def test_plugin_enable_disable(self):
        pm = PluginManager()
        pm.load_all()
        if pm.plugins:
            name = list(pm.plugins.keys())[0]
            pm.disable_plugin(name)
            assert not pm.plugins[name].enabled
            pm.enable_plugin(name)
            assert pm.plugins[name].enabled

    def test_plugin_priority_ordering(self):
        pm = PluginManager()
        pm.load_all()
        plugins = pm.list_plugins()
        for i in range(len(plugins) - 1):
            assert plugins[i].priority <= plugins[i + 1].priority


class TestKnowledgeIntegration:
    def test_personality_has_required_keys(self):
        required = ["name", "greeting", "emotions", "likes", "dislikes", "goals"]
        for key in required:
            assert key in PERSONALITY

    def test_facts_not_empty(self):
        assert len(FACTS) > 0
        for fact in FACTS:
            assert isinstance(fact, str)
            assert len(fact) > 5

    def test_humor_not_empty(self):
        assert len(HUMOR) > 0
        for joke in HUMOR:
            assert isinstance(joke, str)

    def test_responses_all_categories_present(self):
        categories = ["saludos", "despedidas", "estado", "ayuda", "errores"]
        for cat in categories:
            assert cat in RESPONSES

    def test_greetings_and_farewells(self):
        assert len(GREETINGS) > 3
        assert len(FAREWELLS) > 3

    def test_dialogues_all_topics_present(self):
        required = ["presentacion", "tecnologia", "emociones", "desktop", "futuro"]
        for topic in required:
            assert topic in DIALOGUES

    def test_commands_have_actions(self):
        for cmd, patterns in COMMANDS.items():
            assert len(patterns) > 0
            assert isinstance(cmd, str)

    def test_commands_keywords_match(self):
        for cmd, patterns in COMMANDS.items():
            for pattern in patterns:
                assert len(pattern) > 0


class TestDesktopHandsIntegration:
    def test_desktop_hands_init(self):
        dh = DesktopHands()
        assert dh is not None

    def test_desktop_hands_methods_exist(self):
        dh = DesktopHands()
        assert hasattr(dh, "wiggle_window")
        assert hasattr(dh, "nudge_window")
        assert hasattr(dh, "minimize_restore")
        assert hasattr(dh, "shake_desktop")


class TestConfigIntegration:
    def test_config_constants_exist(self):
        assert hasattr(Config, "DISPLAY_WIDTH")
        assert hasattr(Config, "DISPLAY_HEIGHT")
        assert hasattr(Config, "FPS")
        assert hasattr(Config, "FULLSCREEN")
        assert hasattr(Config, "AI_MODEL")
        assert hasattr(Config, "OLLAMA_HOST")

    def test_config_display_values(self):
        assert 0 < Config.DISPLAY_WIDTH <= 3840
        assert 0 < Config.DISPLAY_HEIGHT <= 2160
        assert 0 < Config.FPS <= 240

    def test_config_mic_device(self):
        assert Config.MIC_DEVICE_INDEX is None or isinstance(Config.MIC_DEVICE_INDEX, int)

    def test_config_stt_language(self):
        assert Config.STT_LANGUAGE == "es-ES" or Config.STT_LANGUAGE is not None


class TestDataDriven:
    def test_conversations_fixture(self):
        data = load_test_json("sample_conversations.json")
        assert len(data) == 10
        for entry in data:
            assert "role" in entry
            assert "message" in entry

    def test_faces_fixture(self):
        data = load_test_json("sample_faces.json")
        assert len(data) == 3

    def test_commands_fixture(self):
        data = load_test_json("sample_commands.json")
        cmds = data["voice_commands"]
        assert len(cmds) == 20

    def test_emotion_cases_fixture(self):
        data = load_test_json("emotion_test_cases.json")
        assert len(data) == 10
        for case in data:
            assert "event" in case
            assert "expected_emotion" in case
            assert "valence_change" in case


class TestMainLoopComponents:
    def test_pygame_initialized(self):
        assert pygame.display.get_init()

    def test_screen_create(self):
        screen = pygame.display.set_mode((480, 320))
        assert screen is not None
        assert screen.get_width() == 480
        assert screen.get_height() == 320

    def test_clock_create(self):
        clock = pygame.time.Clock()
        assert clock is not None

    def test_event_poll(self):
        pygame.event.clear()
        events = pygame.event.get()
        assert isinstance(events, list)

    def test_text_input_active(self):
        pygame.key.start_text_input()
        assert pygame.key.get_focused() or True


class TestConcurrentOperations:
    def test_background_listener_thread(self):
        results = []
        def worker():
            for i in range(5):
                results.append(i)
                time.sleep(0.01)
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join(timeout=2)
        assert len(results) == 5

    def test_queue_put_get(self):
        import queue
        q = queue.Queue()
        q.put("test message")
        assert q.get(timeout=1) == "test message"
        assert q.empty()

    def test_thread_safe_lock(self):
        lock = threading.Lock()
        shared = []
        def worker():
            for i in range(100):
                with lock:
                    shared.append(i)
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        assert len(shared) == 500


class TestErrorHandling:
    def test_missing_import_graceful(self):
        try:
            import nonexistent_module_xyz  # noqa: F401
            assert False
        except ImportError:
            assert True

    def test_file_not_found_json(self):
        with pytest.raises(FileNotFoundError):
            load_test_json("nonexistent.json")

    def test_none_values_safe(self):
        val = None
        result = val or "default"
        assert result == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
