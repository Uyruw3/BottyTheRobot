"""
OLED display module — control de pantalla OLED SSD1306/SSH1106.
Incluye emulacion para cuando no hay hardware.
"""

import time
import threading
from botty.config import Config


class OledEmulator:
    """Emulador de pantalla OLED para pruebas sin hardware."""
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.buffer = [[(0, 0, 0)] * width for _ in range(height)]
        self._current_text = ""

    def clear(self):
        self.buffer = [[(0, 0, 0)] * self.width for _ in range(self.height)]
        self._current_text = ""

    def text(self, text, x=0, y=0):
        self._current_text = text

    def show(self):
        pass

    def contrast(self, level):
        pass

    def cleanup(self):
        pass


class OLEDDisplay:
    """Maneja la pantalla OLED con soporte para informacion del robot."""
    def __init__(self):
        self.oled = None
        self._ready = False
        self._width = 128
        self._height = 64
        self._lines = []
        self._max_lines = 6
        self._update_thread = None
        self._running = False
        self._lock = threading.Lock()
        self._mode = "auto"
        self._show_fps = False
        self._fps = 0
        self._info_data = {}

    def init(self):
        try:
            from luma.core.interface.serial import i2c
            from luma.core.render import canvas
            from luma.oled.device import ssd1306, sh1106
            serial = i2c(port=1, address=0x3C)
            self.oled = ssd1306(serial)
            self._width = self.oled.width
            self._height = self.oled.height
            self._ready = True
            print(f"  [OLED] Pantalla {self._width}x{self._height} lista")
        except ImportError:
            print("  [OLED] luma.oled no instalado. Usando emulador.")
            self.oled = OledEmulator(self._width, self._height)
            self._ready = True
        except Exception as e:
            print(f"  [OLED] Error iniciando pantalla: {e}")
            print("  [OLED] Usando emulador.")
            self.oled = OledEmulator(self._width, self._height)
            self._ready = True

        if self._ready:
            self._running = True
            self._update_thread = threading.Thread(target=self._display_loop, daemon=True)
            self._update_thread.start()
        return self._ready

    def _display_loop(self):
        while self._running:
            try:
                if self._ready and self.oled and not isinstance(self.oled, OledEmulator):
                    self._render_display()
            except Exception as e:
                print(f"  [OLED] Error render: {e}")
            time.sleep(0.1)

    def _render_display(self):
        from luma.core.render import canvas
        with canvas(self.oled) as draw:
            draw.rectangle((0, 0, self._width - 1, self._height - 1), outline=255)
            y = 2
            if self._show_fps and self._fps > 0:
                draw.text((2, y), f"FPS: {self._fps}", fill=255)
                y += 10
            with self._lock:
                lines = list(self._lines)
            for line in lines[:self._max_lines]:
                draw.text((2, y), line[:20], fill=255)
                y += 10

    def set_lines(self, lines: list[str]):
        with self._lock:
            self._lines = lines

    def add_line(self, line: str):
        with self._lock:
            self._lines.append(line)
            if len(self._lines) > self._max_lines:
                self._lines = self._lines[-self._max_lines:]

    def update_info(self, data: dict):
        self._info_data = data
        lines = []
        mode = data.get("mode", "?")
        expr = data.get("expression", "?")
        emotion = data.get("emotion", "?")
        battery = data.get("battery", 100)
        user = data.get("current_user", "")
        lines.append(f"Botty v{Config.VERSION}")
        lines.append(f"Modo: {mode}")
        lines.append(f"Expr: {expr}")
        lines.append(f"Emo: {emotion}")
        if user:
            lines.append(f"User: {user}")
        lines.append(f"Bat: {battery}%")
        self.set_lines(lines)

    def show_eyes(self, left_eye_info: dict, right_eye_info: dict):
        lines = []
        if left_eye_info:
            lines.append(f"Ojo I: {left_eye_info.get('expression', '?')}")
        if right_eye_info:
            lines.append(f"Ojo D: {right_eye_info.get('expression', '?')}")
        if len(lines) < 3:
            lines.append(f"Look: {left_eye_info.get('look_x', 0):.1f}, {left_eye_info.get('look_y', 0):.1f}")
        self.set_lines(lines)

    def clear(self):
        if self.oled:
            self.oled.clear()
        with self._lock:
            self._lines.clear()

    def set_mode(self, mode: str):
        self._mode = mode

    def set_fps(self, fps: int):
        self._fps = fps

    def show_fps(self, show: bool = True):
        self._show_fps = show

    def set_contrast(self, level: int):
        if self.oled and hasattr(self.oled, "contrast"):
            self.oled.contrast(max(0, min(255, level)))

    def cleanup(self):
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1)
        if self.oled:
            self.clear()
            self.oled.cleanup()
        self._ready = False


OledDisplay = OLEDDisplay
