"""
Volume Control plugin — sube y baja el volumen del sistema.
"""

from botty.plugins import BasePlugin, PluginEvent


class VolumeControlPlugin(BasePlugin):
    name = "volume_control"
    version = "1.0.0"
    description = "Controla el volumen del sistema por voz"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 7

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "volumen" not in text and "silencio" not in text and "mutear" not in text:
            return None
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            if "silencio" in text or "mutear" in text:
                volume.SetMute(1, None)
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say("Volumen silenciado.")
                return {"muted": True}
            if "sube" in text or "mas" in text or "arriba" in text:
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + 0.15)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(f"Volumen al {int(new_vol * 100)} por ciento.")
                return {"volume": new_vol}
            if "baja" in text or "menos" in text or "abajo" in text:
                current = volume.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - 0.15)
                volume.SetMasterVolumeLevelScalar(new_vol, None)
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(f"Volumen al {int(new_vol * 100)} por ciento.")
                return {"volume": new_vol}
        except ImportError:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("No puedo controlar volumen sin pycaw.")
        except Exception as e:
            return {"error": str(e)}
        return None
