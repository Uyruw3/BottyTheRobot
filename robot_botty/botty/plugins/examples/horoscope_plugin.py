"""
Horoscope plugin — daily horoscopes by zodiac sign.
"""

import random
from botty.plugins import BasePlugin, PluginEvent


class HoroscopePlugin(BasePlugin):
    name = "horoscope"
    version = "1.0.0"
    description = "Proporciona horoscopos diarios por signo zodiacal"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    SIGNS = ["aries", "tauro", "geminis", "cancer", "leo", "virgo",
             "libra", "escorpio", "sagitario", "capricornio", "acuario", "piscis"]

    HOROSCOPES = [
        "Las estrellas alinean energias positivas para ti hoy. Aprovecha para iniciar nuevos proyectos.",
        "La paciencia sera tu mejor aliada hoy. Las cosas buenas toman tiempo.",
        "Un mensaje inesperado podria cambiar tu perspectiva. Manten tu mente abierta.",
        "Tu creatividad esta en su punto maximo. Es un excelente dia para expresarte.",
        "La comunicacion sera clave hoy. No temas decir lo que piensas con claridad.",
        "Las oportunidades financieras pueden aparecer. Manten tus ojos bien abiertos.",
        "Tu energia social esta elevada. Es buen momento para conectar con amigos.",
        "Dedica tiempo a la introspeccion. Las respuestas que buscas estan dentro de ti.",
        "Un cambio inesperado podria traer beneficios a largo plazo. Adaptate con confianza.",
        "La salud y el bienestar merecen tu atencion hoy. Escucha a tu cuerpo.",
        "Una conversation profunda te hara reflexionar sobre temas importantes.",
        "El amor y la amistad brillan hoy. Demuestra tu aprecio a quienes te rodean.",
        "Tu determinacion te llevara lejos. No subestimes el poder de la perseverancia.",
        "Los retos de hoy son las fortalezas de manana. Enfrentalos con valentia.",
        "La suerte favorece a quienes se preparan. Organiza tus ideas y actua.",
        "El equilibrio entre trabajo y descanso es fundamental hoy. No te sobreexijas.",
        "Una idea innovadora podria surgir en el momento menos esperado. Presta atencion.",
        "Tu intuicion esta especialmente aguda hoy. Confia en tu sexto sentido.",
        "Las conexiones que hagas hoy podrian ser importantes a largo plazo.",
        "La gratitud transforma tu perspectiva. Enfocate en lo que tienes, no en lo que falta.",
    ]

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower() if data else ""
        if not any(w in text for w in ["horoscopo", "horoscope", "signo", "zodiaco", "zodiac"]):
            return None
        for sign in self.SIGNS:
            if sign in text:
                h = random.choice(self.HOROSCOPES)
                msg = f"Horoscopo para {sign.capitalize()}: {h}"
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(msg)
                return {"action": "horoscope", "sign": sign, "horoscope": h}
        msg = f"Tu horoscopo dice: {random.choice(self.HOROSCOPES)}"
        if self.robot and self.robot.speaker:
            self.robot.speaker.say(msg)
        return {"action": "horoscope", "sign": "general", "horoscope": msg}
