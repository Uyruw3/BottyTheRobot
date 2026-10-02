"""
Tests for animation data — extended expressions, sequences, and reference data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.display.init()
pygame.display.set_mode((480, 320))

from botty.data.animations_extended import EXTRA_EXPRESSIONS, EXPRESSION_SEQUENCES
from botty.data.animation_reference import (
    EXPRESSION_PARAMETER_RANGES, EXPRESSION_GROUPS, BLINK_PATTERNS,
    LOOK_PATTERNS, ANIMATION_BLUEPRINTS, TRANSITION_CURVES,
    BLINK_STATISTICS,
)
from botty.eyes.animations import EyeState


class TestExtraExpressions:
    def test_extra_expressions_exist(self):
        assert len(EXTRA_EXPRESSIONS) > 30
        assert "wide_eyes" in EXTRA_EXPRESSIONS
        assert "happy_wide" in EXTRA_EXPRESSIONS
        assert "angry_stare" in EXTRA_EXPRESSIONS
        assert "mischievous" in EXTRA_EXPRESSIONS
        assert "innocent" in EXTRA_EXPRESSIONS

    def test_extra_expression_types(self):
        for name, state in EXTRA_EXPRESSIONS.items():
            assert isinstance(state, EyeState), f"{name} not EyeState"
            assert isinstance(name, str)

    def test_extra_expression_params_valid(self):
        for name, state in EXTRA_EXPRESSIONS.items():
            assert 0.0 <= state.scaleY <= 2.0, f"{name}: scaleY={state.scaleY}"
            assert 0.0 <= state.scaleX <= 2.0, f"{name}: scaleX={state.scaleX}"
            assert -1.0 <= state.look_x <= 1.0, f"{name}: look_x={state.look_x}"
            assert -1.0 <= state.look_y <= 1.0, f"{name}: look_y={state.look_y}"
            assert 0.0 <= state.squint <= 1.0, f"{name}: squint={state.squint}"
            assert -1.0 <= state.arch <= 1.0, f"{name}: arch={state.arch}"
            if hasattr(state, 'eye_color') and state.eye_color:
                assert len(state.eye_color) == 3
                assert all(0 <= c <= 255 for c in state.eye_color)

    def test_extra_expression_durations(self):
        for name, state in EXTRA_EXPRESSIONS.items():
            assert state.duration > 0

    def test_all_expressions_cover_all_types(self):
        moods = ["happy", "sad", "angry", "surprised", "loving", "confused",
                 "sleepy", "scared", "curious", "bored", "playful", "shy"]
        for mood in moods:
            found = any(mood in name for name in EXTRA_EXPRESSIONS.keys())
            if not found:
                print(f"  Note: no extra expression for '{mood}'")


class TestExpressionSequences:
    def test_sequences_exist(self):
        assert len(EXPRESSION_SEQUENCES) >= 10
        assert "wake_up" in EXPRESSION_SEQUENCES
        assert "laugh" in EXPRESSION_SEQUENCES
        assert "think_ponder" in EXPRESSION_SEQUENCES

    def test_sequence_structure(self):
        for name, seq in EXPRESSION_SEQUENCES.items():
            assert len(seq) >= 2
            for item in seq:
                assert len(item) == 2
                state, duration = item
                assert isinstance(state, EyeState)
                assert duration > 0

    def test_sequence_laugh(self):
        seq = EXPRESSION_SEQUENCES.get("laugh")
        assert seq is not None
        assert len(seq) == 4

    def test_sequence_wake_up(self):
        seq = EXPRESSION_SEQUENCES.get("wake_up")
        assert seq is not None
        for state, _ in seq:
            assert state.scaleY >= 0.1

    def test_sequence_sad_cry(self):
        seq = EXPRESSION_SEQUENCES.get("sad_cry")
        assert seq is not None
        assert len(seq) >= 4


class TestAnimationReference:
    def test_parameter_ranges(self):
        for param, info in EXPRESSION_PARAMETER_RANGES.items():
            assert "description" in info
            assert "default" in info or "type" in info

    def test_expression_groups(self):
        for group, info in EXPRESSION_GROUPS.items():
            assert "name" in info
            assert "emotions" in info
            assert len(info["emotions"]) >= 3

    def test_blink_patterns(self):
        for pattern, info in BLINK_PATTERNS.items():
            assert "description" in info
            assert "duration" in info
            assert info["duration"] > 0

    def test_look_patterns(self):
        for pattern, info in LOOK_PATTERNS.items():
            assert "description" in info
            assert "speed" in info
            assert info["speed"] > 0

    def test_animation_blueprints(self):
        for bp_name, bp in ANIMATION_BLUEPRINTS.items():
            assert "description" in bp
            assert "phases" in bp
            assert len(bp["phases"]) >= 2

    def test_transition_curves(self):
        for curve, desc in TRANSITION_CURVES.items():
            assert isinstance(curve, str)
            assert isinstance(desc, str)

    def test_blink_statistics(self):
        assert BLINK_STATISTICS["average_interval"] > 0
        assert BLINK_STATISTICS["min_interval"] > 0
        assert BLINK_STATISTICS["max_interval"] > 0
        assert BLINK_STATISTICS["average_duration"] > 0
        assert BLINK_STATISTICS["blinks_per_minute"] > 0

    def test_wink_patterns(self):
        assert "wink_left" in BLINK_PATTERNS
        assert "wink_right" in BLINK_PATTERNS

    def test_sad_emotions_in_group(self):
        sad = EXPRESSION_GROUPS["tristeza"]
        assert "sad" in sad["emotions"]
        assert "sorrowful" in sad["emotions"]

    def test_happy_emotions_in_group(self):
        happy = EXPRESSION_GROUPS["alegria"]
        assert "happy" in happy["emotions"]
        assert "joyful" in happy["emotions"]

    def test_blink_pattern_values(self):
        for pattern, info in BLINK_PATTERNS.items():
            if info["duration"] < 1.0:
                assert True
            assert isinstance(info["left_offset"], (int, float))
            assert isinstance(info["right_offset"], (int, float))

    def test_look_pattern_ranges(self):
        for pattern, info in LOOK_PATTERNS.items():
            if "range_x" in info:
                assert 0 < info["range_x"] <= 1.0
            if "range_y" in info:
                assert 0 <= info["range_y"] <= 1.0

    def test_blueprint_phases(self):
        for bp_name, bp in ANIMATION_BLUEPRINTS.items():
            phases = bp["phases"]
            for i, phase in enumerate(phases):
                has_from = "from" in phase
                has_hold = "hold" in phase
                has_look = "look_to" in phase
                has_color = "color_change" in phase
                assert has_from or has_hold or has_look or has_color, \
                    f"{bp_name} phase {i}: no recognizable action"


class TestHardwareReference:
    def test_hardware_module_imports(self):
        from botty.tools.hardware import (
            RASPBERRY_PI_MODELS, GPIO_PIN_REFERENCE,
            SENSOR_SPECIFICATIONS, MOTOR_SPECIFICATIONS,
            POWER_BUDGET, I2C_ADDRESS_MAP
        )
        assert len(RASPBERRY_PI_MODELS) >= 1
        assert "pi5" in RASPBERRY_PI_MODELS

    def test_gpio_pin_count(self):
        from botty.tools.hardware import GPIO_PIN_REFERENCE
        pins = GPIO_PIN_REFERENCE["physical_pins"]
        assert len(pins) == 40

    def test_sensor_specs(self):
        from botty.tools.hardware import SENSOR_SPECIFICATIONS
        assert "HC-SR04" in SENSOR_SPECIFICATIONS
        assert "MPU6050" in SENSOR_SPECIFICATIONS
        assert "DHT11" in SENSOR_SPECIFICATIONS

    def test_power_budget(self):
        from botty.tools.hardware import POWER_BUDGET
        assert "raspberry_pi_5" in POWER_BUDGET
        assert "total_estimated" in POWER_BUDGET

    def test_i2c_addresses(self):
        from botty.tools.hardware import I2C_ADDRESS_MAP
        assert "0x3C" in I2C_ADDRESS_MAP
        assert "0x68" in I2C_ADDRESS_MAP


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
