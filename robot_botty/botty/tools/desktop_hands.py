"""
Desktop Hands — Botty juega con ventanas del escritorio cuando esta idle.
Mueve, minimiza, restaura y hace wiggle a ventanas.
Solo en Windows.
"""

import sys
import time
import random
import threading

HANDS_AVAILABLE = False
WINDOWS = []

try:
    import pygetwindow as gw
    HANDS_AVAILABLE = True
except ImportError:
    try:
        import win32gui
        import win32con
        WINDOWS = True
    except ImportError:
        pass


def _is_botty_window(title: str) -> bool:
    lower = title.lower()
    return "botty" in lower or "pygame" in lower or "python" in lower


def _get_play_windows():
    """Obtiene ventanas no criticas para jugar."""
    if not HANDS_AVAILABLE:
        return []
    try:
        all_wins = gw.getWindowsWithTitle("")
        playable = []
        for w in all_wins:
            title = w.title.strip()
            if not title:
                continue
            if _is_botty_window(title):
                continue
            if w.isMinimized or not w.visible:
                continue
            if w.width < 100 or w.height < 50:
                continue
            if title.lower() in ("program manager", "windows shell experience host",
                                 "task manager", "task switching", "search", "cortana"):
                continue
            playable.append(w)
        return playable
    except Exception:
        return []


def wiggle_window(window, intensity: float = 1.0):
    """Mueve una ventana rapidamente de lado a lado."""
    try:
        x, y, w, h = window.left, window.top, window.width, window.height
        for i in range(3):
            offset = int(6 * intensity)
            window.moveTo(x + offset, y)
            time.sleep(0.03)
            window.moveTo(x - offset, y)
            time.sleep(0.03)
        window.moveTo(x, y)
    except Exception:
        pass


def nudge_window(window):
    """Empuja una ventana un poco."""
    try:
        x, y, w, h = window.left, window.top, window.width, window.height
        dx = random.choice([-1, 1]) * random.randint(15, 40)
        dy = random.choice([-1, 1]) * random.randint(15, 40)
        new_x = max(0, min(1920 - w, x + dx))
        new_y = max(0, min(1080 - h, y + dy))
        window.moveTo(new_x, new_y)
    except Exception:
        pass


def minimize_restore(window):
    """Minimiza y restaura rapidamente una ventana."""
    try:
        window.minimize()
        time.sleep(0.2)
        window.restore()
        time.sleep(0.1)
    except Exception:
        pass


def shake_desktop(intensity: float = 1.0):
    """Mueve todas las ventanas jugables un poco."""
    windows = _get_play_windows()
    if not windows:
        return
    selected = random.sample(windows, min(len(windows), random.randint(1, 3)))
    for w in selected:
        nudge_window(w)
        time.sleep(0.05)


class DesktopHands:
    def __init__(self):
        self.enabled = HANDS_AVAILABLE
        self._last_action_time = 0
        self._action_cooldown = 2.0
        self._current_target = None
        self._action_thread = None

    def is_available(self) -> bool:
        return self.enabled

    def get_visible_windows(self):
        return _get_play_windows()

    def _is_blacklisted(self, title: str) -> bool:
        if not title or _is_botty_window(title):
            return True
        return title.casefold() in {
            "program manager",
            "task manager",
            "windows shell experience host",
            "task switching",
            "search",
            "cortana",
        }

    def wiggle_window(self, window, intensity: float = 1.0):
        wiggle_window(window, intensity)

    def nudge_window(self, window):
        nudge_window(window)

    def minimize_restore(self, window):
        minimize_restore(window)

    def shake_desktop(self, intensity: float = 1.0):
        shake_desktop(intensity)

    def do_playful_action(self) -> str | None:
        """Ejecuta una accion juguetona con ventanas. Retorna descripcion."""
        if not self.enabled:
            return None
        now = time.time()
        if now - self._last_action_time < self._action_cooldown:
            return None
        self._last_action_time = now

        windows = _get_play_windows()
        if not windows:
            return None

        try:
            w = random.choice(windows)
            self._current_target = w.title
            action = random.random()

            if action < 0.25:
                wiggle_window(w, intensity=random.uniform(0.5, 1.5))
                return f"meneo {w.title}"
            elif action < 0.5:
                nudge_window(w)
                return f"empujo {w.title}"
            elif action < 0.75:
                minimize_restore(w)
                return f"minimizo {w.title}"
            else:
                shake_desktop()
                return "movio varias ventanas"
        except Exception as e:
            return f"error: {e}"

    def get_target_position(self):
        """Retorna (x, y) aproximado de la ventana objetivo para que los ojos miren."""
        if not self.enabled or not self._current_target:
            return None
        try:
            wins = gw.getWindowsWithTitle(self._current_target)
            if wins:
                w = wins[0]
                cx = w.left + w.width // 2
                cy = w.top + w.height // 2
                return (cx, cy)
        except Exception:
            pass
        return None

    def cleanup(self):
        self._current_target = None
