"""
Echo plugin — repite lo que el usuario dice (eco simpatico).
"""

from botty.plugins import BasePlugin, PluginEvent
from botty.eyes.animations import EyeExpression


class EchoPlugin(BasePlugin):
    name = "echo"
    version = "1.0.0"
    description = "Repite lo que dices como eco simpatico"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 100

    def __init__(self, robot=None):
        super().__init__(robot)
        self._echo_enabled = True

    def on_event(self, event: str, data: dict) -> dict | None:
        if not self._echo_enabled:
            return None
        text = data.get("text", "").strip().lower()
        if not text:
            return None
        if "para de repetir" in text or "no hagas eco" in text:
            self._echo_enabled = False
            if self.robot:
                self.robot.speaker.say("Esta bien, no repito mas.")
            return {"action": "echo_disabled"}
        if "repite" in text or "eco" in text:
            words = text.replace("repite ", "").replace("eco ", "").strip()
            if words:
                if self.robot:
                    self.robot.speaker.say(f"Dijiste: {words}")
                    self.robot.eye_renderer.set_expression(EyeExpression.CONFUSED, 3)
                return {"action": "echo_reply", "text": words}
        if self._echo_enabled and len(text) < 20 and "botty" not in text:
            return None
        return None

    def on_unload(self):
        pass


if __name__ == "__main__":
    p = EchoPlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "repite hola mundo"}))
