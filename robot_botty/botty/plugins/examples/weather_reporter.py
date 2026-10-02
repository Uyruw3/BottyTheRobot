"""
Weather Reporter plugin — informa del clima cuando se le pregunta.
Responde al evento VOICE_COMMAND si detecta palabras clave de clima.
"""

import re
from botty.plugins import BasePlugin, PluginEvent


class WeatherReporterPlugin(BasePlugin):
    name = "weather_reporter"
    version = "1.0.0"
    description = "Responde preguntas sobre el clima usando web_search"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 8

    WEATHER_KEYWORDS = [
        "clima", "tiempo", "temperatura", "lluvia", "soleado",
        "frio", "calor", "pronostico", "weather", "temperature",
    ]

    def on_event(self, event: str, data: dict) -> dict | None:
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if not any(kw in text for kw in self.WEATHER_KEYWORDS):
            return None

        if self.robot and self.robot.web_search and self.robot.speaker:
            self.robot.speaker.say("Dejame revisar el clima...")
            result = self.robot.web_search.search_and_format(f"clima {text}")
            if result:
                summary = result[:200]
                self.robot.speaker.say(summary)
                return {"reported": True, "summary": summary}
        return None
