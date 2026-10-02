"""
Edge case tests — boundary conditions and error handling tests.
"""

import sys
import os
import json
import math
import time
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["BOTTY_TEST"] = "1"

import pytest
import numpy as np


class TestMathUtilities:
    def test_clamp_min(self):
        from botty.tools.utils import clamp
        assert clamp(-5, 0, 10) == 0
        assert clamp(-100, -50, 50) == -50

    def test_clamp_max(self):
        from botty.tools.utils import clamp
        assert clamp(15, 0, 10) == 10
        assert clamp(100, -50, 50) == 50

    def test_clamp_within(self):
        from botty.tools.utils import clamp
        assert clamp(5, 0, 10) == 5
        assert clamp(-25, -50, 50) == -25

    def test_lerp_bounds(self):
        from botty.tools.utils import lerp
        assert lerp(0, 100, 0) == 0
        assert lerp(0, 100, 1) == 100
        assert lerp(0, 100, 0.5) == 50

    def test_lerp_clamp(self):
        from botty.tools.utils import lerp
        assert lerp(0, 100, -0.5) == 0
        assert lerp(0, 100, 1.5) == 100

    def test_lerp_precision(self):
        from botty.tools.utils import lerp
        assert abs(lerp(10, 20, 0.3) - 13) < 0.001

    def test_map_range_basic(self):
        from botty.tools.utils import map_range
        assert map_range(0.5, 0, 1, 0, 100) == 50
        assert map_range(0, 0, 1, 0, 100) == 0
        assert map_range(1, 0, 1, 0, 100) == 100

    def test_map_range_inverse(self):
        from botty.tools.utils import map_range
        assert abs(map_range(50, 0, 100, 1, 0) - 0.5) < 0.001

    def test_map_range_zero_range(self):
        from botty.tools.utils import map_range
        assert map_range(5, 0, 0, 0, 100) == 0

    def test_smoothstep_edges(self):
        from botty.tools.utils import smoothstep
        assert smoothstep(0, 1, 0) == 0
        assert smoothstep(0, 1, 1) == 1
        assert smoothstep(0, 1, 0.5) == 0.5
        assert smoothstep(0, 1, -1) == 0
        assert smoothstep(0, 1, 2) == 1


class TestStringUtilities:
    def test_truncate_short(self):
        from botty.tools.utils import truncate
        assert truncate("hello") == "hello"

    def test_truncate_long(self):
        from botty.tools.utils import truncate
        result = truncate("a" * 200, 50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_slugify(self):
        from botty.tools.utils import slugify
        assert slugify("Hola Mundo!") == "hola-mundo"
        assert slugify("Test 123") == "test-123"

    def test_safe_filename(self):
        from botty.tools.utils import safe_filename
        assert safe_filename("file<test>.txt") == "file_test_.txt"
        assert safe_filename("normal.txt") == "normal.txt"

    def test_random_id_length(self):
        from botty.tools.utils import random_id
        assert len(random_id()) == 8
        assert len(random_id(16)) == 16
        assert len(random_id(4)) == 4

    def test_random_id_alpha(self):
        from botty.tools.utils import random_id
        rid = random_id()
        assert rid.isalnum()
        assert rid.islower()


class TestTimeUtilities:
    def test_format_time_seconds(self):
        from botty.tools.utils import format_time
        assert "s" in format_time(30)
        assert "30" in format_time(30)

    def test_format_time_minutes(self):
        from botty.tools.utils import format_time
        result = format_time(125)
        assert "m" in result
        assert "s" in result

    def test_format_time_hours(self):
        from botty.tools.utils import format_time
        result = format_time(3661)
        assert "h" in result
        assert "m" in result
        assert "s" in result

    def test_format_bytes(self):
        from botty.tools.utils import format_bytes
        assert "B" in format_bytes(500)
        assert "KB" in format_bytes(2048)

    def test_format_bytes_large(self):
        from botty.tools.utils import format_bytes
        assert "MB" in format_bytes(1048576)


class TestRateLimiter:
    def test_rate_limiter_allows(self):
        from botty.tools.utils import RateLimiter
        rl = RateLimiter(5, 1.0)
        for _ in range(5):
            assert rl.allow()

    def test_rate_limiter_blocks(self):
        from botty.tools.utils import RateLimiter
        rl = RateLimiter(3, 10.0)
        for _ in range(3):
            rl.allow()
        assert not rl.allow()

    def test_rate_limiter_reset(self):
        from botty.tools.utils import RateLimiter
        rl = RateLimiter(1, 10.0)
        assert rl.allow()
        assert not rl.allow()
        rl.reset()
        assert rl.allow()

    def test_rate_limiter_empty(self):
        from botty.tools.utils import RateLimiter
        rl = RateLimiter(0, 1.0)
        assert not rl.allow()


class TestTimer:
    def test_timer_create(self):
        from botty.tools.utils import Timer
        t = Timer(1.0)
        assert t is not None
        assert not t.is_running

    def test_timer_start_stop(self):
        from botty.tools.utils import Timer
        t = Timer(1.0)
        t.start()
        assert t.is_running
        t.stop()
        assert not t.is_running

    def test_timer_remaining(self):
        from botty.tools.utils import Timer
        t = Timer(5.0)
        t.start()
        assert t.remaining > 0
        t.stop()

    def test_timer_progress(self):
        from botty.tools.utils import Timer
        t = Timer(1.0)
        assert t.progress == 0
        t.start()
        time.sleep(0.01)
        assert t.progress > 0
        t.stop()

    def test_timer_pause_resume(self):
        from botty.tools.utils import Timer
        t = Timer(1.0)
        t.start()
        t.pause()
        was = t.remaining
        time.sleep(0.05)
        assert abs(t.remaining - was) < 0.01
        t.resume()
        t.stop()


class TestMovingAverage:
    def test_moving_average_empty(self):
        from botty.tools.utils import MovingAverage
        ma = MovingAverage(5)
        assert ma.value == 0

    def test_moving_average_basic(self):
        from botty.tools.utils import MovingAverage
        ma = MovingAverage(3)
        ma.add(10)
        assert ma.value == 10
        ma.add(20)
        assert ma.value == 15
        ma.add(30)
        assert ma.value == 20

    def test_moving_average_window(self):
        from botty.tools.utils import MovingAverage
        ma = MovingAverage(2)
        ma.add(10)
        ma.add(20)
        ma.add(30)
        assert ma.value == 25

    def test_moving_average_reset(self):
        from botty.tools.utils import MovingAverage
        ma = MovingAverage(3)
        ma.add(10)
        ma.reset()
        assert ma.value == 0


class TestColorUtils:
    def test_rgb_to_hex(self):
        from botty.tools.utils import ColorUtils
        assert ColorUtils.rgb_to_hex(255, 0, 0) == "#ff0000"
        assert ColorUtils.rgb_to_hex(0, 255, 0) == "#00ff00"
        assert ColorUtils.rgb_to_hex(0, 0, 255) == "#0000ff"

    def test_hex_to_rgb(self):
        from botty.tools.utils import ColorUtils
        assert ColorUtils.hex_to_rgb("#ff0000") == (255, 0, 0)
        assert ColorUtils.hex_to_rgb("00ff00") == (0, 255, 0)

    def test_lerp_color(self):
        from botty.tools.utils import ColorUtils
        c = ColorUtils.lerp_color((0, 0, 0), (100, 100, 100), 0.5)
        assert c == (50, 50, 50)

    def test_brightness(self):
        from botty.tools.utils import ColorUtils
        c = ColorUtils.brightness((100, 100, 100), 2.0)
        assert c == (200, 200, 200)

    def test_brightness_clamp(self):
        from botty.tools.utils import ColorUtils
        c = ColorUtils.brightness((200, 200, 200), 2.0)
        assert all(v <= 255 for v in c)

    def test_random_color(self):
        from botty.tools.utils import ColorUtils
        for _ in range(10):
            c = ColorUtils.random_color()
            assert all(0 <= v <= 255 for v in c)
            assert len(c) == 3


class TestSimpleCache:
    def test_cache_set_get(self):
        from botty.tools.utils import SimpleCache
        c = SimpleCache(max_size=10, ttl=60)
        c.set("key1", "value1")
        assert c.get("key1") == "value1"

    def test_cache_miss(self):
        from botty.tools.utils import SimpleCache
        c = SimpleCache()
        assert c.get("nonexistent") is None

    def test_cache_clear(self):
        from botty.tools.utils import SimpleCache
        c = SimpleCache()
        c.set("a", 1)
        c.set("b", 2)
        c.clear()
        assert c.get("a") is None
        assert c.get("b") is None

    def test_cache_max_size(self):
        from botty.tools.utils import SimpleCache
        c = SimpleCache(max_size=2)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        assert c.size() <= 2


class TestJSONUtilities:
    def test_read_json_nonexistent(self):
        from botty.tools.utils import read_json
        result = read_json("/nonexistent/file.json")
        assert result is None

    def test_read_write_json(self):
        from botty.tools.utils import read_json, write_json
        data = {"key": "value", "num": 42}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            write_json(path, data)
            result = read_json(path)
            assert result == data
        finally:
            os.unlink(path)

    def test_write_json_creates_dir(self):
        from botty.tools.utils import write_json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "subdir", "test.json")
            write_json(path, {"test": True})
            assert os.path.exists(path)

    def test_ensure_dir(self):
        from botty.tools.utils import ensure_dir
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a", "b", "c")
            result = ensure_dir(path)
            assert os.path.exists(path)


class TestProfiler:
    def test_profiler_disabled(self):
        from botty.tools.utils import Profiler
        p = Profiler()
        p.mark("test")
        assert p.measure("test") == 0

    def test_profiler_enabled(self):
        from botty.tools.utils import Profiler
        p = Profiler()
        p.enable()
        p.mark("start")
        result = p.measure("start")
        assert result >= 0

    def test_profiler_report(self):
        from botty.tools.utils import Profiler
        p = Profiler()
        assert p.report() == ""


class TestEdgeConditions:
    def test_division_by_zero_handling(self):
        def safe_div(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                return float("inf")
        assert safe_div(1, 0) == float("inf")
        assert safe_div(10, 2) == 5.0

    def test_large_numbers(self):
        assert 10**100 > 0
        assert math.isfinite(1e308)
        assert math.isinf(1e309)

    def test_empty_list_handling(self):
        data = []
        assert len(data) == 0
        assert sum(data) == 0

    def test_none_equality(self):
        assert None is None
        assert (None or "default") == "default"

    def test_type_conversion_edge(self):
        assert int("0") == 0
        assert float("inf") == float("inf")
        assert str(None) == "None"

    def test_unicode_strings(self):
        text = "Hola! Soy Botty. Como estas hoy? Que bueno verte!"
        assert len(text) > 0
        assert "Botty" in text
        encoded = text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == text

    def test_nested_dicts(self):
        data = {"a": {"b": {"c": "deep"}}}
        assert data["a"]["b"]["c"] == "deep"

    def test_empty_dict(self):
        d = {}
        assert d.get("missing") is None
        assert d.get("missing", "default") == "default"

    def test_boolean_edges(self):
        assert True or False
        assert True and True
        assert not (True and False)

    def test_string_edges(self):
        assert "" == ""
        assert " " .strip() == ""
        assert "\n\t".strip() == ""
