"""
Reminder plugin — recordatorios programados recurrentes.
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from botty.plugins import BasePlugin, PluginEvent


class ReminderPlugin(BasePlugin):
    name = "reminder"
    version = "1.0.0"
    description = "Recordatorios recurrentes programados"
    author = "Botty"
    events = [PluginEvent.VOICE_COMMAND, PluginEvent.TICK]
    priority = 50

    def __init__(self, robot=None):
        super().__init__(robot)
        self._reminders = []
        self._file = os.path.expanduser("~/.botty/reminders.json")
        self._running = True
        self._load()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _load(self):
        try:
            with open(self._file, "r") as f:
                data = json.load(f)
                for r in data:
                    r["next_run"] = datetime.fromisoformat(r["next_run"])
                self._reminders = data
        except (FileNotFoundError, json.JSONDecodeError):
            self._reminders = []

    def _save(self):
        os.makedirs(os.path.dirname(self._file), exist_ok=True)
        data = []
        for r in self._reminders:
            entry = dict(r)
            entry["next_run"] = r["next_run"].isoformat()
            data.append(entry)
        with open(self._file, "w") as f:
            json.dump(data, f, indent=2)

    def on_event(self, event: str, data: dict) -> dict | None:
        text = data.get("text", "").lower()
        if "recuerdame" in text or "recordatorio" in text:
            return self._add_reminder(text)
        if "cancela recordatorio" in text or "elimina recordatorio" in text:
            return self._remove_reminder(text)
        if event == PluginEvent.TICK:
            self._check_reminders()
        return None

    def _add_reminder(self, text: str) -> dict:
        import re
        interval = 3600
        m = re.search(r"cada (\d+)\s*(segundo|minuto|hora|dia|semana)", text)
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            multipliers = {"segundo": 1, "minuto": 60, "hora": 3600, "dia": 86400, "semana": 604800}
            interval = val * multipliers.get(unit, 3600)
        msg = text
        for prefix in ["recuerdame ", "recordatorio "]:
            if prefix in msg:
                msg = msg.split(prefix, 1)[1].strip()
        msg = re.sub(r"cada \d+ (segundo|minuto|hora|dia|semana)", "", msg).strip().capitalize()
        reminder = {
            "message": msg or "Recordatorio",
            "interval": interval,
            "next_run": datetime.now() + timedelta(seconds=min(interval, 60)),
            "active": True
        }
        self._reminders.append(reminder)
        self._save()
        if self.robot:
            self.robot.speaker.say(f"Recordatorio configurado: {msg}")
        return {"action": "reminder_added", "message": msg, "interval": interval}

    def _check_reminders(self):
        now = datetime.now()
        fired = []
        for r in self._reminders:
            if r["active"] and now >= r["next_run"]:
                if self.robot:
                    self.robot.speaker.say(f"Recordatorio: {r['message']}")
                r["next_run"] = now + timedelta(seconds=r["interval"])
                fired.append(r["message"])
        self._save()

    def _remove_reminder(self, text: str) -> dict:
        import re
        m = re.search(r"(\d+)", text)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(self._reminders):
                removed = self._reminders.pop(idx)
                self._save()
                return {"action": "reminder_removed", "message": removed["message"]}
        return {"action": "reminder_error"}

    def get_status(self) -> list:
        return [{"message": r["message"], "next": r["next_run"].isoformat()} for r in self._reminders if r["active"]]

    def on_unload(self):
        self._running = False
        self._save()


if __name__ == "__main__":
    p = ReminderPlugin()
    print(p.on_event(PluginEvent.VOICE_COMMAND, {"text": "recuerdame tomar agua cada 30 minutos"}))
