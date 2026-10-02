"""
Text-to-Speech module — hace hablar al robot.
Soporta pyttsx3 (offline) y gTTS (online).
"""

import os
import tempfile
import threading
from botty.config import Config


class Speaker:
    def __init__(self):
        self.engine = None
        self._is_speaking = False
        self._lock = threading.Lock()

    def init(self):
        if Config.TTS_ENGINE == "gtts":
            try:
                from gtts import gTTS
                self.engine = "gtts"
            except ImportError:
                raise RuntimeError("gTTS no instalado. Usa: pip install gtts")
        else:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", Config.TTS_SPEED)
                self.engine.setProperty("voice", self._find_spanish_voice())
            except ImportError:
                raise RuntimeError("pyttsx3 no instalado. Usa: pip install pyttsx3")

    def _find_spanish_voice(self) -> str | None:
        if hasattr(self.engine, "getProperty"):
            voices = self.engine.getProperty("voices")
            for v in voices:
                if "spanish" in v.name.lower() or "es" in v.id.lower():
                    return v.id
        return None

    def say(self, text: str, block: bool = False):
        if not isinstance(text, str) or not text.strip():
            return False
        if Config.TTS_ENGINE != "gtts" and self.engine is None:
            print("  [TTS] Speaker not initialized; call init() before say().")
            return False
        with self._lock:
            self._is_speaking = True

        if Config.TTS_ENGINE == "gtts":
            self._say_gtts(text, block)
        else:
            self._say_pyttsx3(text, block)

    def _say_pyttsx3(self, text: str, block: bool):
        if block:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            finally:
                self._is_speaking = False
        else:
            def _run():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as exc:
                    print(f"  [TTS] Error al hablar: {exc}")
                finally:
                    self._is_speaking = False
            t = threading.Thread(target=_run, daemon=True)
            t.start()

    def _say_gtts(self, text: str, block: bool):
        from gtts import gTTS
        import pygame

        tts = gTTS(text=text, lang=Config.TTS_LANGUAGE, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            tmp_path = f.name

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        if block:
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.1)

        def _cleanup():
            if block:
                self._is_speaking = False
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        if block:
            _cleanup()
        else:
            def _wait_and_clean():
                while pygame.mixer.music.get_busy():
                    import time
                    time.sleep(0.1)
                _cleanup()
                self._is_speaking = False
            t = threading.Thread(target=_wait_and_clean, daemon=True)
            t.start()

    def is_speaking(self) -> bool:
        return self._is_speaking

    def stop(self):
        if Config.TTS_ENGINE == "gtts":
            import pygame
            pygame.mixer.music.stop()
        elif self.engine and hasattr(self.engine, "stop"):
            try:
                self.engine.stop()
            except Exception:
                pass
        self._is_speaking = False
