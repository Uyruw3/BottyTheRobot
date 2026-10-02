"""
Dice plugin — lanza dados virtuales con resultados aleatorios.
"""

import random
from botty.plugins import BasePlugin, PluginEvent


class DicePlugin(BasePlugin):
    name = "dice"
    version = "1.0.0"
    description = "Lanza dados virtuales (d4, d6, d8, d10, d12, d20, d100)"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 8

    DICE_TYPES = {"d4": 4, "d6": 6, "d8": 8, "d10": 10, "d12": 12, "d20": 20, "d100": 100}

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "dado" not in text and "d20" not in text and "d6" not in text and "tirada" not in text:
            return None
        return self._roll_dice(text)

    def _roll_dice(self, text):
        import re
        for die, sides in self.DICE_TYPES.items():
            if die in text:
                nums = re.findall(r'\d+', text)
                count = 1
                if nums and int(nums[0]) <= 100:
                    count = int(nums[0])
                results = [random.randint(1, sides) for _ in range(count)]
                total = sum(results)
                if count == 1:
                    msg = f"Saco un {results[0]} en {die.upper()}"
                else:
                    msg = f"Resultados: {', '.join(map(str, results))}. Total: {total}"
                if self.robot and self.robot.speaker:
                    self.robot.speaker.say(msg)
                return {"dice": die, "results": results, "total": total}
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("Que dado quieres lanzar? d4, d6, d8, d10, d12, d20 o d100?")
        return None
