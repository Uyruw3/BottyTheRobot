"""
Compliment plugin — da cumplidos aleatorios para animar el dia.
"""

import random
from botty.plugins import BasePlugin, PluginEvent


class ComplimentPlugin(BasePlugin):
    name = "compliment"
    version = "1.0.0"
    description = "Da cumplidos aleatorios para animar el dia"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND, PluginEvent.FACE_RECOGNIZED]
    priority = 4

    COMPLIMENTS = [
        "Tienes una sonrisa contagiosa!",
        "Hoy tienes una energia increible!",
        "Eres mas inteligente que un asistente de IA!",
        "Tu presencia hace que este escritorio sea mejor.",
        "Eres una persona maravillosa, sabes?",
        "Me encanta como piensas!",
        "Eres unico e irrepetible.",
        "Tu creatividad no tiene limites.",
        "Eres el tipo de persona que hace la diferencia.",
        "Tienes un gran sentido del humor!",
        "Eres fuerte, capaz y brillante.",
        "Hiciste un gran trabajo hoy!",
        "El mundo es mejor porque estas en el.",
        "Tu manera de ver la vida es inspiradora.",
        "Eres simplemente increible!",
        "Gracias por ser como eres.",
        "Tienes un corazon enorme.",
        "Eres una luz en este mundo digital.",
        "Tu potencial es ilimitado!",
        "Cada dia que pasa, eres mejor version de ti mismo.",
    ]

    def on_event(self, event, data=None):
        if event == PluginEvent.VOICE_COMMAND:
            text = data.get("text", "").lower()
            if any(w in text for w in ["cumplido", "cumplime", "alago", "motiva",
                                       "animame", "alegrame", "dime algo bonito"]):
                return self._give_compliment()
        elif event == PluginEvent.FACE_RECOGNIZED and random.random() < 0.1:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say(random.choice(self.COMPLIMENTS))
            return {"compliment": True}
        return None

    def _give_compliment(self):
        compliment = random.choice(self.COMPLIMENTS)
        if self.robot and self.robot.speaker:
            self.robot.speaker.say(compliment)
        return {"compliment": compliment}
