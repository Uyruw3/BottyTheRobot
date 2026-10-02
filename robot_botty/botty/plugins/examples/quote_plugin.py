"""
Quote plugin — muestra citas inspiradoras y frases celebres.
"""

import random
from botty.plugins import BasePlugin, PluginEvent


class QuotePlugin(BasePlugin):
    name = "quote"
    version = "1.0.0"
    description = "Muestra citas inspiradoras y frases celebres"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    QUOTES = [
        ("El unico modo de hacer un gran trabajo es amar lo que haces.", "Steve Jobs"),
        ("La vida es lo que pasa mientras estas ocupado haciendo otros planes.", "John Lennon"),
        ("No cuentes los dias, haz que los dias cuenten.", "Muhammad Ali"),
        ("El futuro pertenece a quienes creen en la belleza de sus suenos.", "Eleanor Roosevelt"),
        ("La imaginacion es mas importante que el conocimiento.", "Albert Einstein"),
        ("El exito es ir de fracaso en fracaso sin perder el entusiasmo.", "Winston Churchill"),
        ("Todo lo que alguna vez deseaste esta al otro lado del miedo.", "George Addair"),
        ("No importa lo lento que vayas, mientras no te detengas.", "Confucio"),
        ("Haz lo que puedas, con lo que tengas, donde estes.", "Theodore Roosevelt"),
        ("El unico limite a nuestros logros de manana son nuestras dudas de hoy.", "FDR"),
        ("La mejor manera de predecir el futuro es crearlo.", "Peter Drucker"),
        ("Cree que puedes y ya estas a medio camino.", "Theodore Roosevelt"),
        ("El exito no es definitivo, el fracaso no es fatal: el coraje de continuar es lo que cuenta.", "Churchill"),
        ("La felicidad no es algo hecho, viene de tus propias acciones.", "Dalai Lama"),
        ("S se el cambio que quieres ver en el mundo.", "Mahatma Gandhi"),
        ("Dos caminos se bifurcaban en un bosque, tome el menos transitado.", "Robert Frost"),
        ("La simplicidad es la maxima sofisticacion.", "Leonardo da Vinci"),
        ("El conocimiento habla, pero la sabiduria escucha.", "Jimi Hendrix"),
        ("Puedes tomar mejores decisiones si piensas a largo plazo.", "Jeff Bezos"),
    ]

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "cita" in text or "frase" in text or "inspira" in text or "quote" in text:
            quote, author = random.choice(self.QUOTES)
            msg = f'"{quote}" — {author}'
            if self.robot and self.robot.speaker:
                self.robot.speaker.say(msg)
            return {"quote": quote, "author": author}
        return None
