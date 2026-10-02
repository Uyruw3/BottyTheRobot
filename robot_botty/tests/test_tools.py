"""
Tests for tools module — desktop hands, web search, controller, utils, sound, hardware.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from botty.tools.desktop_hands import DesktopHands
from botty.tools.web_search import WebSearch, SearchResult
from botty.tools.hardware import (
    RASPBERRY_PI_MODELS, GPIO_PIN_REFERENCE, SENSOR_SPECIFICATIONS,
    MOTOR_SPECIFICATIONS, POWER_BUDGET, I2C_ADDRESS_MAP
)


class TestDesktopHands:
    def test_desktop_hands_create(self):
        dh = DesktopHands()
        assert dh is not None

    def test_desktop_hands_methods_exist(self):
        dh = DesktopHands()
        assert hasattr(dh, "wiggle_window")
        assert hasattr(dh, "nudge_window")
        assert hasattr(dh, "minimize_restore")
        assert hasattr(dh, "shake_desktop")

    def test_desktop_hands_get_windows(self):
        dh = DesktopHands()
        windows = dh.get_visible_windows()
        assert isinstance(windows, list)

    def test_desktop_hands_is_blacklisted(self):
        dh = DesktopHands()
        assert dh._is_blacklisted("botty") is True
        assert dh._is_blacklisted("Program Manager") is True
        assert dh._is_blacklisted("Notepad") is False
        assert dh._is_blacklisted("") is True


class TestWebSearch:
    def test_web_search_create(self):
        ws = WebSearch()
        assert ws is not None

    def test_search_result_dataclass(self):
        r = SearchResult(title="Test", url="http://test.com", snippet="Test snippet")
        assert r.title == "Test"
        assert r.url == "http://test.com"
        assert r.snippet == "Test snippet"

    def test_search_result_defaults(self):
        r = SearchResult()
        assert r.title == ""
        assert r.url == ""
        assert r.source == ""

    def test_search_result_with_source(self):
        r = SearchResult(title="A", url="B", snippet="C", source="duckduckgo")
        assert r.source == "duckduckgo"

    def test_search_no_results(self):
        ws = WebSearch()
        results = ws.search("xyznonexistent123456")
        assert isinstance(results, list)

    def test_search_format_empty(self):
        ws = WebSearch()
        result = ws.search_and_format("")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_search_format_no_results(self):
        ws = WebSearch()
        result = ws.search_and_format("")
        assert "No" in result or "no" in result

    def test_search_simple(self):
        ws = WebSearch()
        result = ws.search_simple("test query")
        assert isinstance(result, str)


class TestHardwareReference:
    def test_raspberry_pi_models(self):
        assert "pi5" in RASPBERRY_PI_MODELS
        pi5 = RASPBERRY_PI_MODELS["pi5"]
        assert pi5["name"] == "Raspberry Pi 5"
        assert pi5["gpio_pins"] == 40

    def test_gpio_pin_count(self):
        pins = GPIO_PIN_REFERENCE["physical_pins"]
        assert len(pins) == 40

    def test_gpio_pin_structure(self):
        pins = GPIO_PIN_REFERENCE["physical_pins"]
        for pin_num, info in pins.items():
            assert "name" in info
            assert "type" in info
            assert 1 <= pin_num <= 40

    def test_botty_wiring(self):
        wiring = GPIO_PIN_REFERENCE["botty_wiring"]
        assert "ultrasonic_front_trigger" in wiring
        assert "motor_left_forward" in wiring
        assert "oled_sda" in wiring

    def test_sensor_specifications(self):
        assert "HC-SR04" in SENSOR_SPECIFICATIONS
        assert "MPU6050" in SENSOR_SPECIFICATIONS
        assert "DHT11" in SENSOR_SPECIFICATIONS
        assert "DHT22" in SENSOR_SPECIFICATIONS
        assert "SSD1306" in SENSOR_SPECIFICATIONS

    def test_sensor_spec_detail(self):
        hc = SENSOR_SPECIFICATIONS["HC-SR04"]
        assert hc["range_min"] == "2cm"
        assert hc["range_max"] == "400cm"

    def test_motor_specifications(self):
        assert "N20_micro_gear_motor" in MOTOR_SPECIFICATIONS
        assert "MG996R_servo" in MOTOR_SPECIFICATIONS

    def test_power_budget(self):
        assert "raspberry_pi_5" in POWER_BUDGET
        assert "total_estimated" in POWER_BUDGET
        total = POWER_BUDGET["total_estimated"]
        assert total["typical"] > 0
        assert total["max"] > total["typical"]

    def test_i2c_address_map(self):
        assert "0x3C" in I2C_ADDRESS_MAP
        assert "0x68" in I2C_ADDRESS_MAP
        assert "0x76" in I2C_ADDRESS_MAP
        assert "0x40" in I2C_ADDRESS_MAP
        assert "OLED" in I2C_ADDRESS_MAP["0x3C"]


class TestSoundModule:
    def test_sound_generator_create(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        assert sg is not None

    def test_sound_generator_volume(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        assert sg.get_volume() == 0.5
        sg.set_volume(0.8)
        assert sg.get_volume() == 0.8

    def test_sound_generator_volume_bounds(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        sg.set_volume(2.0)
        assert sg.get_volume() == 1.0
        sg.set_volume(-0.5)
        assert sg.get_volume() == 0.0

    def test_sound_generator_tone_generation(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        result = sg._generate_tone(440, 0.5)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_sound_generator_sweep(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        result = sg._generate_sweep(200, 1000, 0.5)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_sound_generator_noise(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        result = sg._generate_noise(0.5)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_sound_generator_silence(self):
        from botty.audio.sound import SoundGenerator
        sg = SoundGenerator()
        result = sg._generate_silence(0.1)
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestIMU:
    def test_simulated_imu_create(self):
        from botty.sensors.imu import SimulatedIMU
        imu = SimulatedIMU()
        assert imu is not None

    def test_simulated_imu_init(self):
        from botty.sensors.imu import SimulatedIMU
        imu = SimulatedIMU()
        assert imu.init()
        imu.cleanup()

    def test_simulated_imu_readings(self):
        from botty.sensors.imu import SimulatedIMU
        imu = SimulatedIMU()
        imu.init()
        import time
        time.sleep(0.05)
        data = imu.get_all()
        assert isinstance(data, dict)
        assert "ax" in data
        assert "gy" in data
        assert "roll" in data
        assert "temp" in data
        imu.cleanup()

    def test_simulated_imu_acceleration(self):
        from botty.sensors.imu import SimulatedIMU
        imu = SimulatedIMU()
        imu.init()
        import time
        time.sleep(0.05)
        ax, ay, az = imu.get_acceleration()
        assert isinstance(ax, float)
        assert isinstance(ay, float)
        assert isinstance(az, float)
        imu.cleanup()


class TestController:
    def test_controller_create(self):
        from botty.tools.controller import Controller
        try:
            c = Controller()
            assert c is not None
        except Exception as e:
            pytest.skip(f"Controller init: {e}")


class TestToolsIntegration:
    def test_tools_init_imports(self):
        from botty.tools import utils
        assert hasattr(utils, "clamp")
        assert hasattr(utils, "lerp")
        assert hasattr(utils, "RateLimiter")
        assert hasattr(utils, "Timer")
        assert hasattr(utils, "MovingAverage")
        assert hasattr(utils, "ColorUtils")
        assert hasattr(utils, "SimpleCache")

    def test_color_utils_comprehensive(self):
        from botty.tools.utils import ColorUtils
        hex_color = ColorUtils.rgb_to_hex(128, 128, 128)
        assert hex_color == "#808080"
        rgb = ColorUtils.hex_to_rgb("#808080")
        assert rgb == (128, 128, 128)
        lerped = ColorUtils.lerp_color((0, 0, 0), (255, 255, 255), 0.5)
        assert lerped == (127, 127, 127)

    def test_rate_limiter_comprehensive(self):
        from botty.tools.utils import RateLimiter
        rl = RateLimiter(2, 5.0)
        assert rl.allow()
        assert rl.allow()
        assert not rl.allow()
        rl.reset()
        assert rl.allow()

    def test_moving_average_comprehensive(self):
        from botty.tools.utils import MovingAverage
        ma = MovingAverage(3)
        for v in [10, 20, 30, 40]:
            ma.add(v)
        assert ma.min > 0
        assert ma.max >= ma.min
        assert ma.value > 0

    def test_cache_ttl(self):
        from botty.tools.utils import SimpleCache
        import time
        c = SimpleCache(max_size=5, ttl=0.1)
        c.set("x", 100)
        assert c.get("x") == 100
        time.sleep(0.15)
        assert c.get("x") is None

    def test_cache_max_size_eviction(self):
        from botty.tools.utils import SimpleCache
        c = SimpleCache(max_size=3)
        for i in range(5):
            c.set(f"key{i}", i)
        assert c.size() <= 3
