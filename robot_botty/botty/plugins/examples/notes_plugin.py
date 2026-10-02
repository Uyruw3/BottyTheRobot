"""
Notes plugin — guarda y recuerda notas rapidas.
"""

import json
import os
from botty.plugins import BasePlugin, PluginEvent


class NotesPlugin(BasePlugin):
    name = "notes"
    version = "1.0.0"
    description = "Guarda y recuerda notas rapidas"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND]
    priority = 50

    def __init__(self, robot=None):
        super().__init__(robot)
        self._notes = []
        self._notes_file = os.path.expanduser("~/.botty/notes.json")
        self._load()

    def _load(self):
        try:
            with open(self._notes_file, "r") as f:
                self._notes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._notes = []

    def _save(self):
        os.makedirs(os.path.dirname(self._notes_file), exist_ok=True)
        with open(self._notes_file, "w") as f:
            json.dump(self._notes, f, indent=2)

    def on_event(self, event: str, data: dict) -> dict | None:
        text = data.get("text", "").lower()
        if "apunta" in text or "nota" in text or "recuerda" in text:
            return self._save_note(text)
        if "que notas" in text or "mis notas" in text or "recuerdame" in text:
            return self._list_notes()
        if "borra nota" in text or "elimina nota" in text:
            return self._delete_note(text)
        return None

    def _save_note(self, text: str) -> dict:
        for prefix in ["apunta ", "nota ", "recuerda "]:
            if prefix in text:
                note = text.split(prefix, 1)[1].strip().capitalize()
                if note:
                    self._notes.append(note)
                    self._save()
                    return {"action": "note_saved", "note": note}
        return {"action": "note_error", "reason": "no_content"}

    def _list_notes(self) -> dict:
        if not self._notes:
            if self.robot:
                self.robot.speaker.say("No tienes notas guardadas.")
            return {"action": "notes_empty"}
        notes_text = ". ".join(f"{i+1}: {n}" for i, n in enumerate(self._notes[-5:]))
        if self.robot:
            self.robot.speaker.say(f"Tus ultimas notas: {notes_text}")
        return {"action": "notes_list", "count": len(self._notes)}

    def _delete_note(self, text: str) -> dict:
        import re
        m = re.search(r"borra nota (\d+)", text)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(self._notes):
                deleted = self._notes.pop(idx)
                self._save()
                return {"action": "note_deleted", "note": deleted}
        return {"action": "note_delete_error"}

    def on_unload(self):
        self._save()


if __name__ == "__main__":
    p = NotesPlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "apunta comprar leche"}))
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "que notas tengo"}))
