"""
Mood Light plugin — controla una pantalla o LED segun el estado de animo.
"""

from botty.plugins import BasePlugin, PluginEvent
from botty.eyes.animations import EyeExpression


MOOD_COLORS = {
    "happy": (255, 220, 50),
    "sad": (50, 100, 200),
    "angry": (255, 50, 50),
    "surprised": (255, 200, 50),
    "fearful": (150, 50, 150),
    "disgusted": (100, 150, 50),
    "neutral": (100, 100, 100),
    "sleepy": (50, 50, 100),
    "loving": (255, 100, 150),
    "confused": (200, 100, 50),
    "thinking": (100, 150, 200),
    "searching": (50, 150, 200),
    "drive": (255, 50, 0),
    "developer": (0, 255, 100),
    "waking_up": (100, 200, 255),
    "shut_down": (50, 0, 50),
    "talking": (100, 200, 100),
    "listening": (100, 200, 200),
}


class MoodLightPlugin(BasePlugin):
    name = "mood_light"
    version = "1.0.0"
    description = "Controla pantalla/LED segun estado de animo"
    author = "Botty"
    events = [PluginEvent.EYE_EXPRESSION_CHANGED, PluginEvent.EMOTION_CHANGED]
    priority = 20

    def __init__(self, robot=None):
        super().__init__(robot)
        self._current_color = (100, 100, 100)
        self._brightness = 0.5
        self._mode = "auto"

    def on_event(self, event: str, data: dict) -> dict | None:
        if event == PluginEvent.EYE_EXPRESSION_CHANGED:
            expr = data.get("expression", "neutral")
            return self._apply_expression_color(expr)
        elif event == PluginEvent.EMOTION_CHANGED:
            emotion = data.get("emotion", "neutral")
            return self._apply_expression_color(emotion)
        return None

    def _apply_expression_color(self, expr: str) -> dict:
        color = MOOD_COLORS.get(expr, (100, 100, 100))
        self._current_color = color
        if self._mode == "auto" and self.robot:
            pass
        return {"action": "mood_light", "color": color}

    def set_brightness(self, b: float):
        self._brightness = max(0.0, min(1.0, b))

    def set_mode(self, mode: str):
        self._mode = mode

    def get_status(self) -> dict:
        return {
            "color": self._current_color,
            "brightness": self._brightness,
            "mode": self._mode
        }

    def on_unload(self):
        pass


if __name__ == "__main__":
    p = MoodLightPlugin()
    print(p.on_event(PluginEvent.EYE_EXPRESSION_CHANGED, {"expression": "happy"}))
