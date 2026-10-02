"""
Tests for the emotion engine.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from botty.emotion.emotion import EmotionEngine, EmotionState, Mood, EmotionEvent


def test_mood_creation():
    m = Mood(0.5, -0.3)
    assert m.valence == 0.5
    assert m.arousal == -0.3
    print("  OK test_mood_creation")


def test_mood_lerp():
    m = Mood(0.0, 0.0)
    m.lerp(Mood(1.0, 0.5), 0.5)
    assert abs(m.valence - 0.5) < 0.01
    assert abs(m.arousal - 0.25) < 0.01
    print("  OK test_mood_lerp")


def test_mood_clamp():
    m = Mood(2.0, -2.0)
    m.lerp(Mood(0.0, 0.0), 0.1)
    assert m.valence <= 1.0
    assert m.arousal >= -1.0
    print("  OK test_mood_clamp")


def test_dominant_emotion():
    happy_mood = Mood(0.8, 0.5)
    assert happy_mood.dominant_emotion == EmotionState.HAPPY
    sad_mood = Mood(-0.7, -0.4)
    assert sad_mood.dominant_emotion == EmotionState.SAD
    print("  OK test_dominant_emotion")


def test_emotion_engine_create():
    engine = EmotionEngine()
    assert engine.mood is not None
    assert engine.current_emotion is not None
    print("  OK test_emotion_engine_create")


def test_emotion_trigger():
    engine = EmotionEngine()
    initial_valence = engine.mood.valence
    engine.trigger(EmotionEvent.FACE_KNOWN)
    assert engine.mood.valence > initial_valence
    print("  OK test_emotion_trigger")


def test_emotion_decay():
    engine = EmotionEngine(personality_trait="happy")
    engine.trigger(EmotionEvent.USER_GREETED, intensity=2.0)
    high_valence = engine.mood.valence
    for _ in range(600):
        engine.update(1.0 / 60)
    assert engine.mood.valence < high_valence
    print("  OK test_emotion_decay")


def test_personality_set():
    engine = EmotionEngine()
    engine.set_personality("grumpy")
    assert engine.personality == "grumpy"
    assert engine.mood.valence < 0
    print("  OK test_personality_set")


def test_emotion_to_expression():
    assert EmotionState.HAPPY.to_eye_expression().value == "happy"
    assert EmotionState.SAD.to_eye_expression().value == "sad"
    assert EmotionState.SLEEPY.to_eye_expression().value == "sleepy"
    print("  OK test_emotion_to_expression")


def test_mood_report():
    engine = EmotionEngine()
    report = engine.get_mood_report()
    assert "Valence" in report
    assert "Arousal" in report
    print("  OK test_mood_report")


def test_analyze_conversation_positive():
    engine = EmotionEngine()
    engine.analyze_conversation("Eres un excelente robot, te amo!")
    assert engine.mood.valence > 0
    print("  OK test_analyze_conversation_positive")


def test_analyze_conversation_negative():
    robot = EmotionEngine()
    robot.analyze_conversation("Eres un robot malo y feo")
    assert robot.mood.valence < 0.2 or robot.current_emotion in (
        EmotionState.SAD, EmotionState.ANGRY
    )
    print("  OK test_analyze_conversation_negative")


def test_event_cooldown():
    engine = EmotionEngine()
    engine.trigger(EmotionEvent.FACE_KNOWN)
    v1 = engine.mood.valence
    engine.trigger(EmotionEvent.FACE_KNOWN)
    assert abs(engine.mood.valence - v1) < 0.001
    print("  OK test_event_cooldown")


def test_history_limit():
    engine = EmotionEngine()
    for i in range(200):
        engine.trigger(EmotionEvent.FACE_KNOWN)
    assert len(engine._history) <= 100
    print("  OK test_history_limit")


if __name__ == "__main__":
    test_mood_creation()
    test_mood_lerp()
    test_mood_clamp()
    test_dominant_emotion()
    test_emotion_engine_create()
    test_emotion_trigger()
    test_emotion_decay()
    test_personality_set()
    test_emotion_to_expression()
    test_mood_report()
    test_analyze_conversation_positive()
    test_analyze_conversation_negative()
    test_event_cooldown()
    test_history_limit()
    print("\nTodos los tests de emociones pasados!")
