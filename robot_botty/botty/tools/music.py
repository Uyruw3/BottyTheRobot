"""
Music player — busca canciones en YouTube y las reproduce.
Usa yt-dlp para descargar audio y pygame para reproducir.
"""

import os
import threading
import tempfile
import time


class MusicPlayer:
    def __init__(self):
        self._playing = False
        self._stopped = False
        self._thread = None
        self._current_title = ""
        self._temp_file = None

    def is_playing(self) -> bool:
        return self._playing

    def current_song(self) -> str:
        return self._current_title

    def play(self, query: str) -> bool:
        if self._playing:
            self.stop()

        self._stopped = False
        self._thread = threading.Thread(
            target=self._play_thread,
            args=(query,),
            daemon=True,
        )
        self._thread.start()
        return True

    def _play_thread(self, query: str):
        self._playing = True
        self._current_title = query

        try:
            import yt_dlp
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100)

            # ── Search & get best audio URL ──
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "default_search": "ytsearch",
                "max_downloads": 1,
                "format": "bestaudio/best",
                "extract_flat": False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)

                if not info or "entries" not in info or not info["entries"]:
                    print(f"  [Music] No se encontró: {query}")
                    self._playing = False
                    return

                entry = info["entries"][0]
                title = entry.get("title", query)
                self._current_title = title
                webpage_url = entry.get("webpage_url", "")
                duration = entry.get("duration", 0)

                print(f"  [Music] Reproduciendo: {title} ({duration}s)")

                # Find best audio format with a direct URL
                audio_url = None
                for fmt in entry.get("formats", []):
                    if fmt.get("acodec") and fmt.get("acodec") != "none":
                        url = fmt.get("url")
                        if url:
                            audio_url = url
                            break

                if not audio_url:
                    # Fallback: get URL from a secondary extraction
                    ydl_opts2 = {
                        "quiet": True,
                        "no_warnings": True,
                        "format": "bestaudio",
                    }
                    with yt_dlp.YoutubeDL(ydl_opts2) as ydl2:
                        info2 = ydl2.extract_info(webpage_url, download=False)
                        audio_url = info2.get("url")
                        if not audio_url:
                            for fmt in info2.get("formats", []):
                                if fmt.get("acodec") and fmt.get("acodec") != "none":
                                    audio_url = fmt.get("url")
                                    if audio_url:
                                        break

                if not audio_url:
                    print("  [Music] No se pudo obtener URL de audio")
                    self._playing = False
                    return

                # ── Download audio to temp file ──
                tmp = tempfile.NamedTemporaryFile(
                    suffix=".m4a", delete=False
                )
                tmp_path = tmp.name
                tmp.close()
                self._temp_file = tmp_path

                ydl_opts3 = {
                    "quiet": True,
                    "no_warnings": True,
                    "format": "bestaudio",
                    "outtmpl": tmp_path,
                    "extract_audio": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts3) as ydl3:
                    ydl3.download([webpage_url])

                # ── Play with pygame ──
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() and not self._stopped:
                    pygame.time.wait(100)

                pygame.mixer.music.stop()

        except ImportError as e:
            print(f"  [Music] Error: falta librería - {e}")
        except Exception as e:
            print(f"  [Music] Error reproduciendo '{query}': {e}")
        finally:
            self._cleanup_temp()

        self._playing = False
        self._current_title = ""

    def _cleanup_temp(self):
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.unlink(self._temp_file)
            except Exception:
                pass
        self._temp_file = None

    def stop(self):
        self._stopped = True
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        self._playing = False
        self._cleanup_temp()
