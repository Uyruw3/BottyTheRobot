"""
Calculator plugin — evalua expresiones matematicas simples.
"""

import re
import math
from botty.plugins import BasePlugin, PluginEvent


class CalculatorPlugin(BasePlugin):
    name = "calculator"
    version = "1.0.0"
    description = "Evalua expresiones matematicas por voz"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 8

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if not any(w in text for w in ["cuanto es", "calcula", "suma", "resta",
                                        "multiplica", "divide", "elevado", "raiz"]):
            return None
        expr = self._parse_expression(text)
        if expr is None:
            return None
        try:
            result = eval(expr, {"__builtins__": {}}, math.__dict__)
            if isinstance(result, (int, float)):
                msg = f"El resultado es {result:.2f}" if isinstance(result, float) else f"El resultado es {result}"
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(msg)
                return {"expression": expr, "result": result}
        except Exception:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("No pude calcular eso.")
        return None

    def _parse_expression(self, text):
        text = text.replace("cuanto es", "").replace("calcula", "").strip()
        text = text.replace("mas", "+").replace("menos", "-")
        text = text.replace("por", "*").replace("multiplicado por", "*")
        text = text.replace("dividido", "/").replace("entre", "/")
        text = text.replace("elevado a", "**").replace("a la potencia", "**")
        text = text.replace("raiz cuadrada de", "sqrt(").replace("raiz de", "sqrt(")
        text = re.sub(r'(\d+)\s*\+\s*(\d+)', r'\1+\2', text)
        text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', text)
        text = re.sub(r'(\d+)\s*\*\s*(\d+)', r'\1*\2', text)
        text = re.sub(r'(\d+)\s*/\s*(\d+)', r'\1/\2', text)
        text = text.strip().strip('¿?')
        if re.match(r'^[\d+\-*/(). sqrt]+$', text):
            return text
        return None
