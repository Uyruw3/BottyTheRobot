"""
News plugin — provides news summaries and headlines.
"""

import random
from botty.plugins import BasePlugin, PluginEvent


class NewsPlugin(BasePlugin):
    name = "news"
    version = "1.0.0"
    description = "Proporciona resumenes de noticias y titulares"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    SAMPLE_NEWS = [
        "Cientificos descubren una nueva especie de mar profundo en el Oceano Pacifico.",
        "La inteligencia artificial revoluciona el diagnostico medico con un 99% de precision.",
        "Misiones espaciales planean establecer una base lunar permanente para 2035.",
        "El reciclaje de plastico alcanza nuevos record gracias a innovaciones quimicas.",
        "Robots autonomos comienzan a entregar paquetes en zonas urbanas de prueba.",
        "La energia solar se convierte en la fuente mas barata de electricidad en la historia.",
        "Nuevo tratamiento contra el cancer muestra resultados prometedores en ensayos clinicos.",
        "La computacion cuantica da un paso adelante con el procesador mas rapido hasta la fecha.",
        "El cambio climatico acelera la migracion de especies hacia los polos.",
        "Los vehiculos electricos superan en ventas a los de combustion en varios paises europeos.",
    ]

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower() if data else ""
        if not any(w in text for w in ["noticias", "noticia", "news", "que paso", "novedades", "ultimas"]):
            return None
        news = random.choice(self.SAMPLE_NEWS)
        if self.robot and self.robot.speaker:
            self.robot.speaker.say(f"Noticia: {news}")
        return {"action": "news", "headline": news}
