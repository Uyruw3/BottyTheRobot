"""
Alarm plugin — configura alarmas con voz o texto.
"""

import time
import threading
from datetime import datetime, timedelta
from botty.plugins import BasePlugin, PluginEvent


class AlarmPlugin(BasePlugin):
    name = "alarm"
    version = "1.0.0"
    description = "Configura alarmas con voz o texto"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 50

    def __init__(self, robot=None):
        super().__init__(robot)
        self._alarms = []
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def on_event(self, event: str, data: dict) -> dict | None:
        text = data.get("text", "").lower()
        if "alarma" in text or "despiertame" in text or "recordatorio" in text:
            return self._parse_alarm(text)
        return None

    def _parse_alarm(self, text: str) -> dict:
        import re
        minutes = 0
        m = re.search(r"(\d+)\s*minutos?", text)
        if m:
            minutes = int(m.group(1))
        m = re.search(r"(\d+)\s*segundos?", text)
        if m:
            minutes = int(m.group(1)) / 60
        if minutes < 1:
            minutes = 5
        alarm_time = datetime.now() + timedelta(minutes=minutes)
        self._alarms.append({"time": alarm_time, "text": f"Alarma en {int(minutes)} minutos!", "done": False})
        return {"action": "alarm_set", "minutes": minutes}

    def _check_loop(self):
        while self._running:
            now = datetime.now()
            for alarm in self._alarms:
                if not alarm["done"] and now >= alarm["time"]:
                    alarm["done"] = True
                    if self.robot:
                        self.robot.speaker.say(alarm["text"])
                        if hasattr(self.robot, "eye_renderer"):
                            from botty.eyes.animations import EyeExpression
                            self.robot.eye_renderer.set_expression(EyeExpression.SURPRISED, 4)
            self._alarms = [a for a in self._alarms if not a["done"]]
            time.sleep(1)

    def on_unload(self):
        self._running = False


if __name__ == "__main__":
    p = AlarmPlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "alarma en 1 minuto"}))
