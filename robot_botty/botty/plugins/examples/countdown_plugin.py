"""
Countdown plugin — cuenta regresiva para eventos.
"""

import time
import threading
from botty.plugins import BasePlugin, PluginEvent


class CountdownPlugin(BasePlugin):
    name = "countdown"
    version = "1.0.0"
    description = "Cuenta regresiva para eventos"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 50

    def __init__(self, robot=None):
        super().__init__(robot)
        self._countdowns = []
        self._running = True
        self._thread = threading.Thread(target=self._tick, daemon=True)
        self._thread.start()

    def on_event(self, event: str, data: dict) -> dict | None:
        text = data.get("text", "").lower()
        if "cuenta regresiva" in text or "cuenta atras" in text or "temporizador" in text:
            return self._start_countdown(text)
        if "cancela cuenta" in text or "para cuenta" in text:
            return self._cancel_countdown()
        return None

    def _start_countdown(self, text: str) -> dict:
        import re
        seconds = 0
        m = re.search(r"(\d+)\s*segundos?", text)
        if m:
            seconds = int(m.group(1))
        m = re.search(r"(\d+)\s*minutos?", text)
        if m:
            seconds = int(m.group(1)) * 60
        m = re.search(r"(\d+)\s*horas?", text)
        if m:
            seconds = int(m.group(1)) * 3600
        if seconds < 1:
            seconds = 10
        label = "Cuenta regresiva"
        m = re.search(r"para (.+)", text)
        if m:
            label = m.group(1).strip().capitalize()
        cd = {"label": label, "remaining": seconds, "total": seconds, "done": False, "started": time.time()}
        self._countdowns.append(cd)
        if self.robot:
            self.robot.speaker.say(f"Iniciando cuenta regresiva de {seconds} segundos para {label}")
        return {"action": "countdown_started", "label": label, "seconds": seconds}

    def _tick(self):
        while self._running:
            now = time.time()
            for cd in self._countdowns:
                if not cd["done"]:
                    cd["remaining"] = cd["total"] - (now - cd["started"])
                    if cd["remaining"] <= 0:
                        cd["done"] = True
                        cd["remaining"] = 0
                        if self.robot:
                            self.robot.speaker.say(f"Tiempo cumplido para {cd['label']}!")
                            if hasattr(self.robot, "eye_renderer"):
                                from botty.eyes.animations import EyeExpression
                                self.robot.eye_renderer.set_expression(EyeExpression.SURPRISED, 5)
            self._countdowns = [c for c in self._countdowns if not c["done"]]
            time.sleep(0.5)

    def _cancel_countdown(self):
        self._countdowns.clear()
        if self.robot:
            self.robot.speaker.say("Cuentas regresivas canceladas.")
        return {"action": "countdown_cancelled"}

    def get_status(self) -> list:
        return [{"label": c["label"], "remaining": c["remaining"], "total": c["total"]} for c in self._countdowns]

    def on_unload(self):
        self._running = False


if __name__ == "__main__":
    p = CountdownPlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "cuenta regresiva 10 segundos para prueba"}))
