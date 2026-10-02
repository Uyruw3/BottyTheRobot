"""
Face memory — almacena y recuerda caras y nombres de forma persistente.
Usa JSON para almacenar encoding + metadata de cada persona conocida.
"""

import json
import time
import numpy as np
from pathlib import Path
from botty.config import Config


class FaceMemory:
    def __init__(self):
        self.db_path = Path(Config.MEMORY_DB_PATH)
        self.data = {}  # name -> {encodings, first_seen, last_seen, interactions}
        self._loaded = False

    def load(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            try:
                with open(self.db_path) as f:
                    raw = json.load(f)
                self.data = raw
                # Convert encodings back to lists
                for name in self.data:
                    if "encodings" in self.data[name]:
                        self.data[name]["encodings"] = [
                            list(e) for e in self.data[name]["encodings"]
                        ]
                print(f"  [Memoria] Cargados {len(self.data)} recuerdos")
            except Exception as e:
                print(f"  [Memoria] Error cargando: {e}")
                self.data = {}
        else:
            print("  [Memoria] Base de datos nueva")
        self._loaded = True

    def save(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"  [Memoria] Error guardando: {e}")

    def remember(self, name: str, encoding: list[float] | None = None):
        now = time.time()
        if name not in self.data:
            self.data[name] = {
                "encodings": [],
                "first_seen": now,
                "last_seen": now,
                "interactions": 1,
                "notes": "",
            }
        else:
            self.data[name]["last_seen"] = now
            self.data[name]["interactions"] += 1

        if encoding is not None and len(self.data[name]["encodings"]) < 3:
            # Store encoding as list for JSON serialization
            enc = list(encoding) if isinstance(encoding, np.ndarray) else encoding
            if enc not in self.data[name]["encodings"]:
                self.data[name]["encodings"].append(enc)

        self.save()

    def known_names(self) -> list[str]:
        return list(self.data.keys())

    def last_seen(self, name: str) -> float | None:
        if name in self.data:
            return self.data[name]["last_seen"]
        return None

    def interaction_count(self, name: str) -> int:
        if name in self.data:
            return self.data[name]["interactions"]
        return 0

    def get_stored_encodings(self, name: str) -> list[list[float]]:
        if name in self.data:
            return self.data[name].get("encodings", [])
        return []

    def add_note(self, name: str, note: str):
        if name in self.data:
            self.data[name]["notes"] = note
            self.save()

    def get_familiarity(self, name: str) -> str:
        """Devuelve nivel de confianza: desconocido, nuevo, conocido, amigo."""
        if name not in self.data:
            return "desconocido"
        interactions = self.data[name]["interactions"]
        if interactions >= 20:
            return "amigo"
        if interactions >= 5:
            return "conocido"
        return "nuevo"

    def forget(self, name: str):
        if name in self.data:
            del self.data[name]
            self.save()

    def add_face(self, name: str, encoding: list[float] | None = None):
        self.remember(name, encoding)

    def get_face_info(self, name: str) -> dict | None:
        if name not in self.data:
            return None
        info = dict(self.data[name])
        info["familiarity"] = self.get_familiarity(name)
        return info

    def clear(self):
        self.data.clear()
        self.save()

    def get_all_encodings_for_recognition(self) -> tuple[list, list]:
        """Retorna (encodings, names) para usar con face_recognition."""
        encodings = []
        names = []
        for name, info in self.data.items():
            for enc in info.get("encodings", []):
                encodings.append(np.array(enc))
                names.append(name)
        return encodings, names
