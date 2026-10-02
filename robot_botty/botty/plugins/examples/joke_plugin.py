"""
Joke plugin — automaticamente cuenta chistes en momentos random.
"""

import time
import random
from botty.plugins import BasePlugin, PluginEvent
from botty.eyes.animations import EyeExpression


JOKES = [
    "Por que los robots no juegan al escondite? Porque tienen miedo de quedarse sin bateria!",
    "Que le dijo un byte a otro? Nos vemos en el bus de datos!",
    "Como se llama el robot de Bob Esponja? Bob Robot!",
    "Por que los programadores prefieren el modo oscuro? Porque la luz atrae bugs!",
    "Que hace un robot en el desierto? Tomar arena!",
    "Por que los robots son malos bailando? Porque tienen dos pies izquierdos!",
    "Cual es el colmo de un robot? Que lo programen para sentirse solo!",
    "Que le dice un robot a otro robot? Eres mi conexion favorita!",
    "Por que los cientificos no confian en los atomos? Porque lo componen todo!",
    "Como llamas a un robot con mentalidad de tiburon? Roboshark!",
    "Que hace un perro con un taladro? Taladrando!",
    "Por que el libro de matematicas estaba triste? Porque tenia demasiados problemas!",
    "Que hace un pez en el cine? Nada!",
    "Cual es el animal mas antiguo? La cebra, porque esta en blanco y negro!",
    "Por que el sol no toma clases? Porque ya es brillante!",
    "Que le dijo la computadora al teclado? No te voy a presionar!",
    "Como se despide un robot? Hasta la vista, baby!",
    "Que le dijo el 0 al 8? Bonito cinturon!",
    "Por que los fantasmas son malos mintiendo? Porque se les ve a traves!",
    "Que es un robot en una fiesta? Un bailarin programado!",
    "Por que los robots no pueden comer? Porque tienen la comida en la memoria!",
    "Cual es el superpoder de un robot? El Ctrl+Z de la vida!",
    "Como se dice robot en chino? Robot Chino!",
    "Que le dijo un semaforo a otro? No me mires, me estoy cambiando!",
    "Por que las tortugas no usan internet? Porque tienen caparazon!",
]


class JokePlugin(BasePlugin):
    name = "joke"
    version = "1.0.0"
    description = "Cuenta chistes automaticamente"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND, PluginEvent.TICK]
    priority = 30

    def __init__(self, robot=None):
        super().__init__(robot)
        self._last_joke_time = 0
        self._joke_cooldown = 120
        self._told_jokes = set()

    def on_event(self, event: str, data: dict) -> dict | None:
        if event == PluginEvent.VOICE_COMMAND:
            text = data.get("text", "").lower()
            if "chiste" in text or "hazme reir" in text or "cuenta algo" in text:
                return self._tell_random_joke()
        elif event == PluginEvent.TICK:
            now = time.time()
            if now - self._last_joke_time > self._joke_cooldown and random.random() < 0.005:
                return self._tell_random_joke()
        return None

    def _tell_random_joke(self) -> dict:
        available = [j for j in JOKES if j not in self._told_jokes]
        if not available:
            self._told_jokes.clear()
            available = JOKES
        joke = random.choice(available)
        self._told_jokes.add(joke)
        self._last_joke_time = time.time()
        if self.robot:
            self.robot.speaker.say(joke)
            if hasattr(self.robot, "eye_renderer"):
                self.robot.eye_renderer.set_expression(EyeExpression.HAPPY, 6)
        return {"action": "tell_joke", "joke": joke}


if __name__ == "__main__":
    p = JokePlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "cuentame un chiste"}))
