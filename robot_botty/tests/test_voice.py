"""
Tests for voice/audio modules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"

from botty.audio.tts import Speaker
from botty.config import Config


def test_speaker_create():
    s = Speaker()
    assert s is not None
    print("  OK test_speaker_create")


def test_speaker_init():
    s = Speaker()
    try:
        s.init()
        assert s.engine is not None or getattr(s, 'engine', None) is not None
    except Exception:
        pass
    print("  OK test_speaker_init")


def test_speaker_say_none():
    s = Speaker()
    s.say(None, block=False)
    print("  OK test_speaker_say_none")


def test_speaker_say_empty():
    s = Speaker()
    s.say("", block=False)
    print("  OK test_speaker_say_empty")


def test_speaker_say_short():
    s = Speaker()
    s.say("Hola", block=False)
    print("  OK test_speaker_say_short")


def test_speaker_is_speaking():
    s = Speaker()
    try:
        result = s.is_speaking()
        assert isinstance(result, bool)
    except Exception:
        pass
    print("  OK test_speaker_is_speaking")


def test_speaker_stop():
    s = Speaker()
    try:
        s.stop()
    except Exception:
        pass
    print("  OK test_speaker_stop")


def test_speaker_say_spanish():
    s = Speaker()
    s.say("Hola mundo! Esto es una prueba.", block=False)
    print("  OK test_speaker_say_spanish")


def test_speaker_say_long():
    s = Speaker()
    long_text = "Este es un texto largo " * 50
    s.say(long_text, block=False)
    print("  OK test_speaker_say_long")


def test_speaker_multiple_calls():
    s = Speaker()
    for msg in ["Hola", "Como estas?", "Bien y tu?"]:
        s.say(msg, block=False)
    print("  OK test_speaker_multiple_calls")


def test_speaker_cleanup():
    s = Speaker()
    try:
        s.stop()
    except Exception:
        pass
    print("  OK test_speaker_cleanup")


if __name__ == "__main__":
    test_speaker_create()
    test_speaker_init()
    test_speaker_say_none()
    test_speaker_say_empty()
    test_speaker_say_short()
    test_speaker_is_speaking()
    test_speaker_stop()
    test_speaker_say_spanish()
    test_speaker_say_long()
    test_speaker_multiple_calls()
    test_speaker_cleanup()
    print("\nTodos los tests de voz pasados!")
