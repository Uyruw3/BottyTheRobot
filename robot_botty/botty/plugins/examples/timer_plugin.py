"""
Timer plugin — temporizador y alarmas por voz.
"""

import time
import threading
from botty.plugins import BasePlugin, PluginEvent


class TimerPlugin(BasePlugin):
    name = "timer"
    version = "1.0.0"
    description = "Temporizador y alarmas con aviso por voz"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 6

    def __init__(self, robot=None):
        super().__init__(robot)
        self.timers = []

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "timer" in text or "temporizador" in text or "alarma" in text or "recordatorio" in text:
            return self._handle_timer(text)
        return None

    def _handle_timer(self, text):
        import re
        nums = re.findall(r'\d+', text)
        if not nums:
            return None
        seconds = int(nums[0])
        if "minuto" in text or "min" in text:
            seconds *= 60
        elif "hora" in text:
            seconds *= 3600
        if seconds > 86400:
            return None
        if self.robot and self.robot.speaker:
            self.robot.speaker.say(f"Temporizador puesto para {seconds} segundos.")
        t = threading.Timer(seconds, self._alarm)
        t.daemon = True
        t.start()
        self.timers.append(t)
        return {"timer_set": seconds}

    def _alarm(self):
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("Ring ring! El temporizador ha terminado!")
