"""
Tests for motors module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from botty.movement.motors import Motors
from botty.config import Config


def test_motors_create():
    m = Motors()
    assert m is not None
    print("  OK test_motors_create")


def test_motors_init():
    m = Motors()
    try:
        m.init()
    except Exception:
        pass
    print("  OK test_motors_init")


def test_motors_forward():
    m = Motors()
    m.forward(50)
    print("  OK test_motors_forward")


def test_motors_backward():
    m = Motors()
    m.backward(50)
    print("  OK test_motors_backward")


def test_motors_turn_left():
    m = Motors()
    m.turn_left(50)
    print("  OK test_motors_turn_left")


def test_motors_turn_right():
    m = Motors()
    m.turn_right(50)
    print("  OK test_motors_turn_right")


def test_motors_stop():
    m = Motors()
    m.stop()
    print("  OK test_motors_stop")


def test_motors_drive():
    m = Motors()
    m.drive(50, -50)
    m.drive(0, 0)
    print("  OK test_motors_drive")


def test_motors_speed_range():
    m = Motors()
    for speed in [0, 25, 50, 75, 100]:
        m.forward(speed)
    print("  OK test_motors_speed_range")


def test_motors_cleanup():
    m = Motors()
    try:
        m.cleanup()
    except Exception:
        pass
    print("  OK test_motors_cleanup")


def test_motors_multiple_drives():
    m = Motors()
    for _ in range(5):
        m.drive(30, -30)
        m.drive(-30, 30)
        m.stop()
    print("  OK test_motors_multiple_drives")


if __name__ == "__main__":
    test_motors_create()
    test_motors_init()
    test_motors_forward()
    test_motors_backward()
    test_motors_turn_left()
    test_motors_turn_right()
    test_motors_stop()
    test_motors_drive()
    test_motors_speed_range()
    test_motors_cleanup()
    test_motors_multiple_drives()
    print("\nTodos los tests de motores pasados!")
