"""
Password generator plugin — generates secure random passwords.
"""

import random
import string
from botty.plugins import BasePlugin, PluginEvent


class PasswordPlugin(BasePlugin):
    name = "password_generator"
    version = "1.0.0"
    description = "Genera contrasenas seguras aleatorias"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower() if data else ""
        if not any(w in text for w in ["contrasena", "password", "clave", "password_gen"]):
            return None
        length = self._parse_length(text)
        pw = self._generate(length)
        msg = f"Tu contrasena generada es: {pw}"
        if self.robot and self.robot.speaker:
            self.robot.speaker.say(msg)
        return {"action": "generate_password", "password": pw, "length": length}

    def _parse_length(self, text):
        words = text.split()
        for i, w in enumerate(words):
            if w.isdigit() and 4 <= int(w) <= 64:
                return int(w)
        return 16

    def _generate(self, length=16):
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return "".join(random.choice(chars) for _ in range(length))
