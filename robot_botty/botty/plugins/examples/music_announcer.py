"""
Music Announcer plugin — anuncia los cambios de cancion.
"""

from botty.plugins import BasePlugin, PluginEvent
from botty.eyes.animations import EyeExpression


class MusicAnnouncerPlugin(BasePlugin):
    name = "music_announcer"
    version = "1.0.0"
    description = "Anuncia cuando empieza o termina una cancion"
    author = "Botty"
    events = [PluginEvent.MUSIC_STARTED, PluginEvent.MUSIC_STOPPED]
    priority = 5

    def on_event(self, event: str, data: dict) -> dict | None:
        if event == PluginEvent.MUSIC_STARTED:
            song = data.get("song", "una cancion")
            if self.robot:
                self.robot.speaker.say(f"Poniendo {song}")
                self.robot.eye_renderer.set_expression(EyeExpression.HAPPY, 4)
            return {"announced": True, "song": song}

        elif event == PluginEvent.MUSIC_STOPPED:
            if self.robot:
                self.robot.speaker.say("Musica parada.")
                self.robot.eye_renderer.set_expression(EyeExpression.IDLE, 4)
            return {"announced": True}
        return None
