"""
Screenshot plugin — captura la pantalla cuando se le pide.
"""

import os
import time
from pathlib import Path
from botty.plugins import BasePlugin, PluginEvent


class ScreenshotPlugin(BasePlugin):
    name = "screenshot"
    version = "1.0.0"
    description = "Captura la pantalla y guarda la imagen"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 7

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "captura" in text or "screenshot" in text or "pantalla" in text:
            return self._take_screenshot()
        return None

    def _take_screenshot(self):
        try:
            import pyautogui
            shots_dir = Path.home() / ".botty" / "screenshots"
            shots_dir.mkdir(parents=True, exist_ok=True)
            filename = f"botty_capture_{int(time.time())}.png"
            path = str(shots_dir / filename)
            pyautogui.screenshot(path)
            if self.robot and self.robot.speaker:
                self.robot.speaker.say(f"Captura guardada como {filename}")
            return {"saved": filename}
        except ImportError:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("Necesito pyautogui para capturar pantalla.")
            return {"error": "pyautogui not installed"}
        except Exception as e:
            return {"error": str(e)}
