"""
Wallpaper Changer plugin — cambia el fondo de pantalla.
"""

import os
import random
import ctypes
from pathlib import Path
from botty.plugins import BasePlugin, PluginEvent


class WallpaperChangerPlugin(BasePlugin):
    name = "wallpaper_changer"
    version = "1.0.0"
    description = "Cambia el fondo de pantalla del escritorio"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    WALLPAPER_DIR = str(Path.home() / "Pictures" / "botty_wallpapers")

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "fondo" in text or "wallpaper" in text or "pantalla" in text:
            return self._change_wallpaper(text)
        return None

    def _change_wallpaper(self, text):
        if "cambia" in text or "pon" in text or "nuevo" in text or "aleatorio" in text:
            if os.path.isdir(self.WALLPAPER_DIR):
                images = [f for f in os.listdir(self.WALLPAPER_DIR)
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    chosen = os.path.join(self.WALLPAPER_DIR, random.choice(images))
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, chosen, 3)
                    if self.robot and self.robot.speaker:
                        self.robot.speaker.say("Fondo de pantalla cambiado!")
                    return {"wallpaper": chosen}
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("No tengo imagenes en la carpeta de wallpapers.")
        return None
