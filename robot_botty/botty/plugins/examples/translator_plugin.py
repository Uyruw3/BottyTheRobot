"""
Translator plugin — traduce texto entre idiomas.
"""

from botty.plugins import BasePlugin, PluginEvent


class TranslatorPlugin(BasePlugin):
    name = "translator"
    version = "1.0.0"
    description = "Traduce texto entre idiomas usando la web"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 5

    def on_event(self, event, data=None):
        if event != PluginEvent.VOICE_COMMAND:
            return None
        text = data.get("text", "").lower()
        if "traduce" in text or "translate" in text or "traduccion" in text:
            return self._translate(text, data.get("text", ""))
        return None

    def _translate(self, text, original):
        if "al ingles" in text or "to english" in text:
            target = "ingles"
            lang_pair = "en"
        elif "al espanol" in text or "to spanish" in text:
            target = "espanol"
            lang_pair = "es"
        else:
            target = "espanol"
            lang_pair = "es"
        query = original.lower().replace("traduce", "").replace("traduccion", "")
        query = query.replace("al ingles", "").replace("al espanol", "").strip()
        if not query:
            if self.robot and self.robot.speaker:
                self.robot.speaker.say("Que texto quieres que traduzca?")
            return None
        if self.robot and self.robot.web_search:
            result = self.robot.web_search.search_and_format(
                f"traducir '{query}' al {target}"
            )
            if result:
                self.robot.speaker.say(f"La traduccion es: {result[:150]}")
                return {"translated": result[:150]}
        if self.robot and self.robot.speaker:
            self.robot.speaker.say("No pude traducir eso ahora.")
        return None
