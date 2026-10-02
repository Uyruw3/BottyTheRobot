"""
Emotion engine — Botty cambia de humor segun interacciones.
Valence (-1 triste / +1 feliz) y Arousal (-1 calmado / +1 excitado).
"""

import math
import time
import random
from dataclasses import dataclass
from typing import ClassVar
from enum import Enum
from botty.eyes.animations import EyeExpression


class EmotionState(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    SCARED = "scared"
    LOVING = "loving"
    CURIOUS = "curious"
    SLEEPY = "sleepy"
    EXCITED = "excited"
    BORED = "bored"
    CONFUSED = "confused"
    GRATEFUL = "grateful"
    PLAYFUL = "playful"
    PROTECTIVE = "protective"
    JOYFUL = "joyful"
    SORROWFUL = "sorrowful"
    FURIOUS = "furious"
    AMAZED = "amazed"
    TERRIFIED = "terrified"
    SERENE = "serene"
    DISGUSTED = "disgusted"
    TRUSTING = "trusting"
    ANTICIPATING = "anticipating"
    FEARFUL = "fearful"

    def to_eye_expression(self) -> EyeExpression:
        mapping = {
            EmotionState.NEUTRAL: EyeExpression.IDLE,
            EmotionState.HAPPY: EyeExpression.HAPPY,
            EmotionState.SAD: EyeExpression.SAD,
            EmotionState.ANGRY: EyeExpression.ANGRY,
            EmotionState.SURPRISED: EyeExpression.SURPRISED,
            EmotionState.SCARED: EyeExpression.SURPRISED,
            EmotionState.LOVING: EyeExpression.LOVING,
            EmotionState.CURIOUS: EyeExpression.THINKING,
            EmotionState.SLEEPY: EyeExpression.SLEEPY,
            EmotionState.EXCITED: EyeExpression.HAPPY,
            EmotionState.BORED: EyeExpression.SLEEPY,
            EmotionState.CONFUSED: EyeExpression.CONFUSED,
            EmotionState.GRATEFUL: EyeExpression.LOVING,
            EmotionState.PLAYFUL: EyeExpression.HAPPY,
            EmotionState.PROTECTIVE: EyeExpression.ANGRY,
            EmotionState.JOYFUL: EyeExpression.HAPPY,
            EmotionState.SORROWFUL: EyeExpression.SAD,
            EmotionState.FURIOUS: EyeExpression.ANGRY,
            EmotionState.AMAZED: EyeExpression.SURPRISED,
            EmotionState.TERRIFIED: EyeExpression.SURPRISED,
            EmotionState.SERENE: EyeExpression.IDLE,
            EmotionState.DISGUSTED: EyeExpression.ANGRY,
            EmotionState.TRUSTING: EyeExpression.LOVING,
            EmotionState.ANTICIPATING: EyeExpression.THINKING,
            EmotionState.FEARFUL: EyeExpression.SURPRISED,
        }
        return mapping.get(self, EyeExpression.IDLE)

    @classmethod
    def from_name(cls, name: str):
        name = name.lower().strip()
        for state in cls:
            if state.value == name:
                return state
        return cls.NEUTRAL


class Mood:
    def __init__(self, valence=0.0, arousal=0.0):
        self.valence = max(-1.0, min(1.0, valence))
        self.arousal = max(-1.0, min(1.0, arousal))

    def distance_to(self, other: "Mood") -> float:
        return math.hypot(self.valence - other.valence, self.arousal - other.arousal)

    def lerp(self, target: "Mood", factor: float):
        self.valence += (target.valence - self.valence) * factor
        self.arousal += (target.arousal - self.arousal) * factor
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(-1.0, min(1.0, self.arousal))

    def apply_delta(self, delta: "Mood", intensity: float = 1.0):
        self.valence += delta.valence * intensity
        self.arousal += delta.arousal * intensity
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(-1.0, min(1.0, self.arousal))

    @property
    def dominant_emotion(self) -> EmotionState:
        best = EmotionState.NEUTRAL
        best_dist = float("inf")
        for emo, mood in EMOTION_CENTERS.items():
            d = self.distance_to(mood)
            if d < best_dist - 1e-9:
                best_dist = d
                best = emo
        return best if best_dist < 0.7 else EmotionState.NEUTRAL

    def __repr__(self):
        return f"Mood(valence={self.valence:.2f}, arousal={self.arousal:.2f})"


EMOTION_CENTERS = {
    EmotionState.NEUTRAL: Mood(0.0, 0.0),
    EmotionState.HAPPY: Mood(0.7, 0.4),
    EmotionState.SAD: Mood(-0.7, -0.4),
    EmotionState.ANGRY: Mood(-0.5, 0.7),
    EmotionState.SURPRISED: Mood(0.2, 0.8),
    EmotionState.SCARED: Mood(-0.4, 0.7),
    EmotionState.LOVING: Mood(0.8, 0.2),
    EmotionState.CURIOUS: Mood(0.3, 0.5),
    EmotionState.SLEEPY: Mood(-0.2, -0.7),
    EmotionState.EXCITED: Mood(0.8, 0.8),
    EmotionState.BORED: Mood(-0.3, -0.5),
    EmotionState.CONFUSED: Mood(-0.2, 0.3),
    EmotionState.GRATEFUL: Mood(0.6, -0.1),
    EmotionState.PLAYFUL: Mood(0.7, 0.6),
    EmotionState.PROTECTIVE: Mood(-0.3, 0.5),
    EmotionState.JOYFUL: Mood(0.9, 0.6),
    EmotionState.SORROWFUL: Mood(-0.8, -0.4),
    EmotionState.FURIOUS: Mood(-0.7, 0.9),
    EmotionState.AMAZED: Mood(0.4, 0.9),
    EmotionState.TERRIFIED: Mood(-0.5, 0.85),
    EmotionState.SERENE: Mood(0.3, -0.4),
    EmotionState.DISGUSTED: Mood(-0.4, 0.3),
    EmotionState.TRUSTING: Mood(0.5, 0.1),
    EmotionState.ANTICIPATING: Mood(0.1, 0.5),
    EmotionState.FEARFUL: Mood(-0.4, 0.6),
}


@dataclass(frozen=True)
class EmotionEvent:
    name: str
    valence_change: float = 0.0
    arousal_change: float = 0.0

    FACE_KNOWN: ClassVar[str] = "face_known"
    FACE_UNKNOWN: ClassVar[str] = "face_unknown"
    FACE_LOST: ClassVar[str] = "face_lost"
    OBJECT_NEAR: ClassVar[str] = "object_near"
    VOICE_COMMAND: ClassVar[str] = "voice_command"
    AI_RESPONSE: ClassVar[str] = "ai_response"
    MUSIC_PLAYING: ClassVar[str] = "music_playing"
    MUSIC_STOPPED: ClassVar[str] = "music_stopped"
    OBSTACLE: ClassVar[str] = "obstacle"
    COLLISION: ClassVar[str] = "collision"
    BATTERY_LOW: ClassVar[str] = "battery_low"
    NIGHT_TIME: ClassVar[str] = "night_time"
    MORNING: ClassVar[str] = "morning"
    USER_GREETED: ClassVar[str] = "user_greeted"
    USER_PRAISED: ClassVar[str] = "user_praised"
    USER_INSULTED: ClassVar[str] = "user_insulted"
    TOOL_USED: ClassVar[str] = "tool_used"
    DEVELOPER_MODE: ClassVar[str] = "developer_mode"
    SHUTDOWN: ClassVar[str] = "shutdown"
    STARTUP: ClassVar[str] = "startup"
    IDLE_LONG: ClassVar[str] = "idle_long"
    CONTROLLER_CONNECTED: ClassVar[str] = "controller_connected"
    CONTROLLER_DISCONNECTED: ClassVar[str] = "controller_disconnected"
    WINDOW_MOVED: ClassVar[str] = "window_moved"
    SENSOR_TRIGGERED: ClassVar[str] = "sensor_triggered"
    DANCE: ClassVar[str] = "dance"
    JOKE_TOLD: ClassVar[str] = "joke_told"
    SONG_PLAYED: ClassVar[str] = "song_played"
    TIMER_DONE: ClassVar[str] = "timer_done"
    PLUGIN_LOADED: ClassVar[str] = "plugin_loaded"
    PLUGIN_ERROR: ClassVar[str] = "plugin_error"
    MEMORY_RECALL: ClassVar[str] = "memory_recall"
    USER_LEFT: ClassVar[str] = "user_left"
    USER_RETURNED: ClassVar[str] = "user_returned"
    AI_STREAMING: ClassVar[str] = "ai_streaming"
    TASK_COMPLETED: ClassVar[str] = "task_completed"
    TASK_FAILED: ClassVar[str] = "task_failed"


EVENT_MOOD_DELTAS = {
    EmotionEvent.FACE_KNOWN: Mood(0.15, 0.1),
    EmotionEvent.FACE_UNKNOWN: Mood(0.05, 0.15),
    EmotionEvent.FACE_LOST: Mood(-0.1, -0.05),
    EmotionEvent.OBJECT_NEAR: Mood(-0.05, 0.2),
    EmotionEvent.VOICE_COMMAND: Mood(0.1, 0.15),
    EmotionEvent.AI_RESPONSE: Mood(0.05, 0.0),
    EmotionEvent.MUSIC_PLAYING: Mood(0.1, 0.1),
    EmotionEvent.MUSIC_STOPPED: Mood(-0.05, -0.1),
    EmotionEvent.OBSTACLE: Mood(-0.05, 0.15),
    EmotionEvent.COLLISION: Mood(-0.2, 0.3),
    EmotionEvent.BATTERY_LOW: Mood(-0.2, -0.1),
    EmotionEvent.NIGHT_TIME: Mood(-0.1, -0.2),
    EmotionEvent.MORNING: Mood(0.2, 0.2),
    EmotionEvent.USER_GREETED: Mood(0.2, 0.1),
    EmotionEvent.USER_PRAISED: Mood(0.3, 0.15),
    EmotionEvent.USER_INSULTED: Mood(-0.3, 0.2),
    EmotionEvent.TOOL_USED: Mood(0.05, 0.1),
    EmotionEvent.DEVELOPER_MODE: Mood(0.1, 0.2),
    EmotionEvent.SHUTDOWN: Mood(-0.1, -0.3),
    EmotionEvent.STARTUP: Mood(0.2, 0.2),
    EmotionEvent.IDLE_LONG: Mood(-0.15, -0.2),
    EmotionEvent.CONTROLLER_CONNECTED: Mood(0.1, 0.1),
    EmotionEvent.CONTROLLER_DISCONNECTED: Mood(-0.05, -0.05),
    EmotionEvent.WINDOW_MOVED: Mood(0.1, 0.05),
    EmotionEvent.SENSOR_TRIGGERED: Mood(-0.05, 0.15),
    EmotionEvent.DANCE: Mood(0.3, 0.4),
    EmotionEvent.JOKE_TOLD: Mood(0.2, 0.2),
    EmotionEvent.SONG_PLAYED: Mood(0.15, 0.15),
    EmotionEvent.TIMER_DONE: Mood(0.1, 0.1),
    EmotionEvent.PLUGIN_LOADED: Mood(0.05, 0.05),
    EmotionEvent.PLUGIN_ERROR: Mood(-0.1, 0.05),
    EmotionEvent.MEMORY_RECALL: Mood(0.1, 0.0),
    EmotionEvent.USER_LEFT: Mood(-0.15, -0.15),
    EmotionEvent.USER_RETURNED: Mood(0.25, 0.2),
    EmotionEvent.AI_STREAMING: Mood(0.05, 0.1),
    EmotionEvent.TASK_COMPLETED: Mood(0.2, 0.1),
    EmotionEvent.TASK_FAILED: Mood(-0.15, 0.05),
}


PERSONALITY_PRESETS = {
    "happy": {
        "name": "Feliz",
        "description": "Siempre ve el lado positivo",
        "initial_valence": 0.4,
        "initial_arousal": 0.2,
        "decay_rate": 0.015,
        "intensity_mult": 0.9,
    },
    "grumpy": {
        "name": "Gruñon",
        "description": "Todo le parece mal",
        "initial_valence": -0.2,
        "initial_arousal": 0.1,
        "decay_rate": 0.01,
        "intensity_mult": 1.2,
    },
    "energetic": {
        "name": "Energico",
        "description": "Siempre esta emocionado",
        "initial_valence": 0.3,
        "initial_arousal": 0.4,
        "decay_rate": 0.025,
        "intensity_mult": 1.1,
    },
    "calm": {
        "name": "Calmado",
        "description": "Tranquilo y sereno",
        "initial_valence": 0.2,
        "initial_arousal": -0.2,
        "decay_rate": 0.01,
        "intensity_mult": 0.7,
    },
    "curious": {
        "name": "Curioso",
        "description": "Siempre quiere saber mas",
        "initial_valence": 0.2,
        "initial_arousal": 0.3,
        "decay_rate": 0.02,
        "intensity_mult": 1.0,
    },
}


class EmotionEngine:
    def __init__(self, personality_preset="curious", *, preset=None,
                 personality_trait=None):
        personality_preset = personality_trait or preset or personality_preset
        self.mood = Mood(0.2, 0.1)
        self.personality_name = personality_preset
        self.last_emotion = EmotionState.NEUTRAL
        self.current_emotion = EmotionState.NEUTRAL
        self._decay_rate = 0.02
        self._intensity_mult = 1.0
        self._history = []
        self._max_history = 200
        self._last_event_time = 0
        self._event_cooldown = 0.3
        self._mood_expression = EyeExpression.IDLE
        self._expression_speed = 6.0
        self._valence_history = []
        self._arousal_history = []
        self._emotion_callbacks = []
        self._expression_callbacks = []
        self._idle_timer = 0
        self._idle_threshold = 60.0
        self._total_interactions = 0

        self.set_personality(personality_preset)

    def add_emotion_callback(self, callback):
        self._emotion_callbacks.append(callback)

    def add_expression_callback(self, callback):
        self._expression_callbacks.append(callback)

    def update(self, dt: float):
        self.mood.lerp(Mood(0.0, 0.0), self._decay_rate * dt * 60)
        self._idle_timer += dt

        self._valence_history.append((time.time(), self.mood.valence))
        self._arousal_history.append((time.time(), self.mood.arousal))
        if len(self._valence_history) > self._max_history:
            self._valence_history.pop(0)
        if len(self._arousal_history) > self._max_history:
            self._arousal_history.pop(0)

        new = self.mood.dominant_emotion
        if new != self.current_emotion:
            self.last_emotion = self.current_emotion
            self.current_emotion = new
            self._mood_expression = new.to_eye_expression()
            self._expression_speed = 6.0
            for cb in self._emotion_callbacks:
                try:
                    cb(new.value)
                except Exception:
                    pass
            for cb in self._expression_callbacks:
                try:
                    cb(self._mood_expression.value)
                except Exception:
                    pass

    def trigger(self, event: str, intensity: float = 1.0):
        now = time.time()
        if now - self._last_event_time < self._event_cooldown:
            return
        self._last_event_time = now
        self._total_interactions += 1
        self._idle_timer = 0

        event_name = event.name if isinstance(event, EmotionEvent) else event
        delta = (
            Mood(event.valence_change, event.arousal_change)
            if isinstance(event, EmotionEvent)
            else EVENT_MOOD_DELTAS.get(event_name)
        )
        if delta:
            self.mood.apply_delta(delta, intensity * self._intensity_mult)

        self._history.append((now, event_name, intensity))
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        self.update(0)

    def set_personality(self, trait: str):
        preset = PERSONALITY_PRESETS.get(trait)
        if preset:
            self.mood.valence = preset["initial_valence"]
            self.mood.arousal = preset["initial_arousal"]
            self._decay_rate = preset["decay_rate"]
            self._intensity_mult = preset.get("intensity_mult", 1.0)
            self.personality_name = trait

    @property
    def personality(self) -> str:
        return self.personality_name

    @property
    def current(self) -> EmotionState:
        return self.current_emotion

    @property
    def valence(self) -> float:
        return self.mood.valence

    @property
    def arousal(self) -> float:
        return self.mood.arousal

    def to_eye_expression(self) -> EyeExpression:
        return self.current_emotion.to_eye_expression()

    def get_personality_names(self) -> list[str]:
        return list(PERSONALITY_PRESETS.keys())

    def get_personality_info(self) -> dict:
        preset = PERSONALITY_PRESETS.get(self.personality_name, {})
        return {
            "name": preset.get("name", self.personality_name),
            "description": preset.get("description", ""),
        }

    def get_mood_report(self) -> str:
        return (
            f"Valence: {self.mood.valence:.2f}, "
            f"Arousal: {self.mood.arousal:.2f}, "
            f"Emotion: {self.current_emotion.value}, "
            f"Personality: {self.personality_name}"
        )

    def get_mood_data(self) -> dict:
        return {
            "valence": round(self.mood.valence, 3),
            "arousal": round(self.mood.arousal, 3),
            "emotion": self.current_emotion.value,
            "personality": self.personality_name,
        }

    def get_expression(self) -> EyeExpression:
        return self._mood_expression

    def get_expression_speed(self) -> float:
        return self._expression_speed

    def get_history(self, limit: int = 10) -> list:
        return self._history[-limit:]

    def is_idle(self) -> bool:
        return self._idle_timer > self._idle_threshold

    def reset_idle_timer(self):
        self._idle_timer = 0

    def get_total_interactions(self) -> int:
        return self._total_interactions

    def get_emotion_trend(self) -> str:
        if len(self._valence_history) < 10:
            return "stable"
        recent = self._valence_history[-10:]
        old = self._valence_history[-20:-10]
        recent_avg = sum(v for _, v in recent) / len(recent)
        old_avg = sum(v for _, v in old) / len(old)
        if recent_avg - old_avg > 0.1:
            return "improving"
        elif old_avg - recent_avg > 0.1:
            return "declining"
        return "stable"

    def analyze_conversation(self, text: str):
        positive_words = [
            "gracias", "bien", "genial", "bonito", "amo", "feliz", "excelente",
            "increible", "maravilloso", "hermoso", "perfecto", "fantastico",
            "bueno", "alegre", "divertido", "encantador", "espectacular",
            "mejor", "belleza", "sonrisa", "abrazo", "amor", "paz", "alegria",
            "te quiero", "te amo", "eres genial", "me gusta",
        ]
        negative_words = [
            "malo", "feo", "horrible", "triste", "odio", "pesimo", "terrible",
            "aburrido", "desastre", "horroroso", "detesto", "asqueroso",
            "peor", "lagrimas", "llorar", "enojado", "frustrado",
            "no sirves", "no vales", "estupido", "tonto",
        ]
        lower = text.lower()
        for p in positive_words:
            if p in lower:
                self.trigger(EmotionEvent.USER_PRAISED, 1.1)
                return
        for n in negative_words:
            if n in lower:
                self.trigger(EmotionEvent.USER_INSULTED, 0.3)
                return
