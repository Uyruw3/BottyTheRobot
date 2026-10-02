"""
Pomodoro Plugin — temporizador de productividad con tecnica Pomodoro.
"""

import time
import threading
from botty.plugins import BasePlugin, PluginEvent


class PomodoroPlugin(BasePlugin):
    name = "pomodoro"
    version = "1.0.0"
    description = "Tecnica Pomodoro para productividad"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 6

    def __init__(self, robot=None):
        super().__init__(robot)
        self._running = False
        self._pomodoros = 0

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "pomodoro" in text or "productividad" in text or "trabajo" in text:
            return self._start_pomodoro()
        return None

    def _start_pomodoro(self):
        if self._running:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("Ya hay un pomodoro en curso.")
            return None
        self._running = True
        t = threading.Thread(target=self._pomodoro_cycle, daemon=True)
        t.start()
        return {"pomodoro_started": True}

    def _pomodoro_cycle(self):
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("Pomodoro iniciado! 25 minutos de enfoque.")
        time.sleep(1500)
        if not self._running:
            return
        self._pomodoros += 1
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("Pomodoro completado! Toma un descanso de 5 minutos.")
        time.sleep(300)
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("Descanso terminado! Listo para el siguiente pomodoro.")
        self._running = False
