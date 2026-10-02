"""
Utility functions — helpers for Botty prototype.
"""

import os
import sys
import json
import time
import math
import random
import string
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)


def map_range(value, in_min, in_max, out_min, out_max):
    in_range = in_max - in_min
    out_range = out_max - out_min
    if in_range == 0:
        return out_min
    return out_min + ((value - in_min) / in_range) * out_range


def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def random_id(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def timestamp():
    return datetime.now().isoformat()


def time_ms():
    return int(time.time() * 1000)


def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def format_bytes(bytes_val):
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


def truncate(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def slugify(text):
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def safe_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        filename = filename.replace(c, "_")
    return filename.strip(". ")


def ensure_dir(path):
    Path(path).expanduser().mkdir(parents=True, exist_ok=True)
    return str(Path(path).expanduser())


def read_json(path):
    try:
        with open(Path(path).expanduser(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_json(path, data, indent=2):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_project_root():
    return Path(__file__).parent.parent.parent


def get_data_dir():
    return ensure_dir("~/.botty")


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self._lock:
            self._calls = [t for t in self._calls if now - t < self.period]
            if len(self._calls) >= self.max_calls:
                return False
            self._calls.append(now)
            return True

    def reset(self):
        with self._lock:
            self._calls.clear()


class Timer:
    def __init__(self, duration: float, callback=None):
        self.duration = duration
        self.callback = callback
        self._start = 0
        self._running = False
        self._paused = False
        self._elapsed = 0

    def start(self):
        self._start = time.time()
        self._running = True
        self._paused = False
        self._elapsed = 0

    def stop(self):
        self._running = False
        self._paused = False

    def pause(self):
        if self._running and not self._paused:
            self._elapsed += time.time() - self._start
            self._paused = True

    def resume(self):
        if self._paused:
            self._start = time.time()
            self._paused = False

    def update(self) -> bool:
        if not self._running or self._paused:
            return False
        elapsed = self._elapsed + (time.time() - self._start)
        if elapsed >= self.duration:
            self._running = False
            if self.callback:
                self.callback()
            return True
        return False

    @property
    def remaining(self) -> float:
        if not self._running:
            return 0
        elapsed = self._elapsed
        if not self._paused:
            elapsed += time.time() - self._start
        return max(0, self.duration - elapsed)

    @property
    def progress(self) -> float:
        if not self._running:
            return 0
        elapsed = self._elapsed
        if not self._paused:
            elapsed += time.time() - self._start
        return clamp(elapsed / self.duration, 0, 1)

    @property
    def is_running(self) -> bool:
        return self._running


class MovingAverage:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self._values = []
        self._lock = threading.Lock()

    def add(self, value):
        with self._lock:
            self._values.append(value)
            if len(self._values) > self.window_size:
                self._values.pop(0)

    @property
    def value(self):
        with self._lock:
            if not self._values:
                return 0.0
            return sum(self._values) / len(self._values)

    @property
    def min(self):
        with self._lock:
            return min(self._values) if self._values else 0.0

    @property
    def max(self):
        with self._lock:
            return max(self._values) if self._values else 0.0

    def reset(self):
        with self._lock:
            self._values.clear()


class FPSMonitor:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self._times = []
        self._lock = threading.Lock()

    def tick(self):
        now = time.time()
        with self._lock:
            self._times.append(now)
            if len(self._times) > self.window_size:
                self._times.pop(0)

    @property
    def fps(self):
        with self._lock:
            if len(self._times) < 2:
                return 0
            elapsed = self._times[-1] - self._times[0]
            if elapsed <= 0:
                return 0
            return (len(self._times) - 1) / elapsed

    def reset(self):
        with self._lock:
            self._times.clear()


class ColorUtils:
    @staticmethod
    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def lerp_color(c1, c2, t):
        t = clamp(t, 0.0, 1.0)
        return (
            int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)),
        )

    @staticmethod
    def brightness(color, factor):
        factor = clamp(factor, 0.0, 2.0)
        return (
            min(255, int(color[0] * factor)),
            min(255, int(color[1] * factor)),
            min(255, int(color[2] * factor)),
        )

    @staticmethod
    def random_color():
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))


class Profiler:
    def __init__(self):
        self._marks = {}
        self._timers = {}
        self._enabled = False

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def mark(self, name):
        if not self._enabled:
            return
        self._marks[name] = time.time()

    def measure(self, name):
        if not self._enabled or name not in self._marks:
            return 0
        return (time.time() - self._marks[name]) * 1000

    def start_timer(self, name):
        if not self._enabled:
            return
        self._timers[name] = time.time()

    def stop_timer(self, name):
        if not self._enabled or name not in self._timers:
            return 0
        elapsed = (time.time() - self._timers[name]) * 1000
        return elapsed

    def report(self):
        if not self._enabled:
            return ""
        lines = ["=== Profiler Report ==="]
        now = time.time()
        for name, t in sorted(self._marks.items()):
            lines.append(f"  {name}: {(now - t) * 1000:.1f}ms")
        return "\n".join(lines)


class SimpleCache:
    def __init__(self, max_size=100, ttl=300):
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry["time"] < self._ttl:
                    return entry["value"]
                del self._cache[key]
            return None

    def set(self, key, value):
        with self._lock:
            if len(self._cache) >= self._max_size:
                oldest = min(self._cache.keys(), key=lambda k: self._cache[k]["time"])
                del self._cache[oldest]
            self._cache[key] = {"value": value, "time": time.time()}

    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self):
        with self._lock:
            return len(self._cache)
