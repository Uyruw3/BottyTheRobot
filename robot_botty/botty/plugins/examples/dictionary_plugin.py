"""
Dictionary plugin — word definitions and translations.
"""

from botty.plugins import BasePlugin, PluginEvent


class DictionaryPlugin(BasePlugin):
    name = "dictionary"
    version = "1.0.0"
    description = "Define palabras y proporciona sinonimos"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    WORD_DEFINITIONS = {
        "robot": "Maquina programable capaz de realizar tareas de forma autonoma o semi-autonoma.",
        "algoritmo": "Conjunto de instrucciones paso a paso para resolver un problema.",
        "inteligencia": "Capacidad de adquirir y aplicar conocimientos y habilidades.",
        "python": "Lenguaje de programacion interpretado, de alto nivel y proposito general.",
        "algoritmo": "Secuencia finita de reglas para resolver un problema especifico.",
        "datos": "Informacion representada en forma adecuada para su tratamiento por computadora.",
        "software": "Conjunto de programas, instrucciones y datos que componen un sistema informatico.",
        "hardware": "Parte fisica y tangible de un sistema informatico.",
        "red": "Conjunto de dispositivos interconectados que comparten recursos e informacion.",
        "nube": "Servicios informaticos accesibles a traves de internet sin gestion directa del usuario.",
    }

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower() if data else ""
        if not any(w in text for w in ["define", "definicion", "que significa", "meaning", "significado"]):
            return None
        for word, definition in self.WORD_DEFINITIONS.items():
            if word in text:
                msg = f"{word.capitalize()}: {definition}"
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(msg)
                return {"action": "define", "word": word, "definition": definition}
        return None
