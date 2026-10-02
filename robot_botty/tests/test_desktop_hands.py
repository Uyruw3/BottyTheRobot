"""
Tests for desktop hands module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from botty.tools.desktop_hands import DesktopHands, HANDS_AVAILABLE, _get_play_windows


def test_hands_availability():
    assert isinstance(HANDS_AVAILABLE, bool)
    print("  OK test_hands_availability")


def test_desktop_hands_create():
    h = DesktopHands()
    assert h is not None
    assert isinstance(h.enabled, bool)
    print("  OK test_desktop_hands_create")


def test_is_available():
    h = DesktopHands()
    if h.enabled:
        assert h.is_available() is True
    print("  OK test_is_available")


def test_get_play_windows():
    wins = _get_play_windows()
    assert isinstance(wins, list)
    print("  OK test_get_play_windows")


def test_do_playful_action():
    h = DesktopHands()
    if h.enabled:
        result = h.do_playful_action()
        if result:
            assert isinstance(result, str)
    print("  OK test_do_playful_action")


def test_do_playful_action_cooldown():
    h = DesktopHands()
    if not h.enabled:
        print("  OK test_do_playful_action_cooldown (skip)")
        return
    h.do_playful_action()
    result = h.do_playful_action()
    assert result is None
    print("  OK test_do_playful_action_cooldown")


def test_get_target_position():
    h = DesktopHands()
    if h.enabled:
        pos = h.get_target_position()
        if pos:
            assert len(pos) == 2
    print("  OK test_get_target_position")


def test_cleanup():
    h = DesktopHands()
    h.cleanup()
    assert h._current_target is None
    print("  OK test_cleanup")


def test_wiggle_window_none():
    from botty.tools.desktop_hands import wiggle_window
    wiggle_window(None)
    print("  OK test_wiggle_window_none")


def test_nudge_window_none():
    from botty.tools.desktop_hands import nudge_window
    nudge_window(None)
    print("  OK test_nudge_window_none")


def test_minimize_restore_none():
    from botty.tools.desktop_hands import minimize_restore
    minimize_restore(None)
    print("  OK test_minimize_restore_none")


if __name__ == "__main__":
    test_hands_availability()
    test_desktop_hands_create()
    test_is_available()
    test_get_play_windows()
    test_do_playful_action()
    test_do_playful_action_cooldown()
    test_get_target_position()
    test_cleanup()
    test_wiggle_window_none()
    test_nudge_window_none()
    test_minimize_restore_none()
    print("\nTodos los tests de desktop hands pasados!")
