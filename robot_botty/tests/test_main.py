"""
Tests for main module — BottyRobot class structure.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.display.init()
pygame.display.set_mode((480, 320))

from botty.main import BottyRobot, clamp


def test_robot_create():
    r = BottyRobot()
    assert r is not None
    print("  OK test_robot_create")


def test_robot_initial_state():
    r = BottyRobot()
    assert r.running == False
    assert r.current_user is None
    assert r._auto_mode == True
    assert r._developer_mode == False
    assert r._fleeing == False
    assert r._pushing == False
    assert r._mouse_reaction_timer == 0.0
    print("  OK test_robot_initial_state")


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(0, -5, 5) == 0
    assert clamp(-10, -5, 5) == -5
    print("  OK test_clamp")


def test_robot_has_components():
    r = BottyRobot()
    assert hasattr(r, "eye_renderer")
    assert hasattr(r, "speaker")
    assert hasattr(r, "brain")
    assert hasattr(r, "motors")
    assert hasattr(r, "camera")
    assert hasattr(r, "memory")
    assert hasattr(r, "desktop_hands")
    print("  OK test_robot_has_components")


def test_robot_has_modes():
    r = BottyRobot()
    assert hasattr(r, "_auto_mode")
    assert hasattr(r, "_developer_mode")
    assert hasattr(r, "controller_drive")
    print("  OK test_robot_has_modes")


def test_robot_has_voice_queue():
    r = BottyRobot()
    assert hasattr(r, "_voice_queue")
    assert hasattr(r, "_listener_thread")
    assert hasattr(r, "_listener_running")
    print("  OK test_robot_has_voice_queue")


def test_robot_has_mouse_state():
    r = BottyRobot()
    assert hasattr(r, "_mouse_x")
    assert hasattr(r, "_mouse_y")
    assert hasattr(r, "_mouse_reaction_timer")
    print("  OK test_robot_has_mouse_state")


def test_robot_has_idle_behavior():
    r = BottyRobot()
    assert hasattr(r, "_idle_behavior_timer")
    assert hasattr(r, "_idle_complaints")
    assert hasattr(r, "_touch_reactions")
    assert len(r._idle_complaints) > 0
    assert len(r._touch_reactions) > 0
    print("  OK test_robot_has_idle_behavior")


def test_robot_expression_state():
    r = BottyRobot()
    assert hasattr(r, "_prev_expression")
    print("  OK test_robot_expression_state")


def test_robot_timers():
    r = BottyRobot()
    assert r.last_face_seen == 0
    assert r.last_interaction == 0
    assert r._lockout_timer == 0.0
    assert r._avoid_timer == 0.0
    assert r._explore_timer == 0.0
    print("  OK test_robot_timers")


def test_robot_faces():
    r = BottyRobot()
    assert r.face_lost_timeout == 5.0
    assert r._owner_name is not None
    print("  OK test_robot_faces")


def test_robot_dangerous_keywords():
    from botty.config import Config
    assert len(Config.DEVELOPER_DANGEROUS_KEYWORDS) > 0
    print("  OK test_robot_dangerous_keywords")


if __name__ == "__main__":
    test_robot_create()
    test_robot_initial_state()
    test_clamp()
    test_robot_has_components()
    test_robot_has_modes()
    test_robot_has_voice_queue()
    test_robot_has_mouse_state()
    test_robot_has_idle_behavior()
    test_robot_expression_state()
    test_robot_timers()
    test_robot_faces()
    test_robot_dangerous_keywords()
    print("\nTodos los tests de main pasados!")
