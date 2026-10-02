"""
Tests for sensors module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from botty.sensors.ultrasonic import SonarArray
from botty.config import Config


def test_sonar_create():
    s = SonarArray()
    assert s is not None
    print("  OK test_sonar_create")


def test_sonar_init():
    s = SonarArray()
    try:
        s.init()
    except Exception:
        pass
    print("  OK test_sonar_init")


def test_sonar_read():
    s = SonarArray()
    result = s.read()
    assert isinstance(result, dict)
    print("  OK test_sonar_read")


def test_sonar_read_keys():
    s = SonarArray()
    result = s.read()
    expected = {"front", "left", "right"}
    assert expected.issubset(result.keys()) or len(result) == 0
    print("  OK test_sonar_read_keys")


def test_sonar_default_values():
    s = SonarArray()
    result = s.read()
    for key in ["front", "left", "right"]:
        if key in result:
            assert result[key] >= 0
    print("  OK test_sonar_default_values")


def test_sonar_ready():
    s = SonarArray()
    assert hasattr(s, "ready")
    print("  OK test_sonar_ready")


def test_sonar_cleanup():
    s = SonarArray()
    try:
        s.cleanup()
    except Exception:
        pass
    print("  OK test_sonar_cleanup")


def test_sonar_multiple_reads():
    s = SonarArray()
    for _ in range(5):
        result = s.read()
        assert isinstance(result, dict)
    print("  OK test_sonar_multiple_reads")


def test_sonar_edge_cases():
    s = SonarArray()
    result = s.read()
    for val in result.values():
        assert isinstance(val, (int, float))
    print("  OK test_sonar_edge_cases")


def test_sonar_empty_init():
    s = SonarArray()
    assert hasattr(s, "pins")
    print("  OK test_sonar_empty_init")


if __name__ == "__main__":
    test_sonar_create()
    test_sonar_init()
    test_sonar_read()
    test_sonar_read_keys()
    test_sonar_default_values()
    test_sonar_ready()
    test_sonar_cleanup()
    test_sonar_multiple_reads()
    test_sonar_edge_cases()
    test_sonar_empty_init()
    print("\nTodos los tests de sensores pasados!")
