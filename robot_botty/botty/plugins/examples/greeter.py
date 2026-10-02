"""
Greeter plugin — saluda automaticamente cuando detecta caras conocidas.
"""

import time
from botty.plugins import BasePlugin, PluginEvent
from botty.eyes.animations import EyeExpression


class GreeterPlugin(BasePlugin):
    name = "greeter"
    version = "1.0.0"
    description = "Saluda automaticamente a caras conocidas y desconocidas"
    author = "Botty"
    events = [PluginEvent.FACE_RECOGNIZED, PluginEvent.FACE_LOST]
    priority = 10

    def __init__(self, robot=None):
        super().__init__(robot)
        self._greeted = set()
        self._last_greet_time = 0
        self._greet_cooldown = 30

    def on_event(self, event: str, data: dict) -> dict | None:
        if event == PluginEvent.FACE_RECOGNIZED:
            return self._on_face(data)
        elif event == PluginEvent.FACE_LOST:
            return self._on_face_lost()
        return None

    def _on_face(self, data: dict):
        name = data.get("name", "Desconocido")
        now = time.time()
        if now - self._last_greet_time < self._greet_cooldown:
            return {"action": "skip"}
        self._last_greet_time = now

        if name == "Desconocido":
            if name not in self._greeted:
                self._greeted.add(name)
                if self.robot:
                    self.robot.speaker.say(
                        "Hola! No te conozco. Presiona espacio para presentarte."
                    )
                return {"action": "greeted_unknown"}
        else:
            self._greeted.add(name)
            if self.robot:
                familiarity = "amigo"
                if self.robot.memory:
                    familiarity = self.robot.memory.get_familiarity(name)
                if familiarity in ("amigo", "conocido"):
                    self.robot.speaker.say(f"Que bueno verte de nuevo, {name}!")
                    self.robot.eye_renderer.set_expression(EyeExpression.HAPPY, 6)
                else:
                    self.robot.speaker.say(f"Hola {name}! Como estas hoy?")
            return {"action": "greeted", "name": name}
        return None

    def _on_face_lost(self):
        self._greeted.discard("Desconocido")
        return {"action": "forgot_unknown"}
