"""
Tests for eye renderer and animations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

pygame.display.init()
pygame.display.set_mode((480, 320))

from botty.eyes.animations import EyeExpression, EyeState, EXPRESSIONS
from botty.eyes.renderer import EyeRenderer


def test_all_expressions_present():
    required = [
        EyeExpression.IDLE, EyeExpression.HAPPY, EyeExpression.SAD,
        EyeExpression.ANGRY, EyeExpression.SURPRISED, EyeExpression.SLEEPY,
        EyeExpression.TALKING, EyeExpression.LISTENING, EyeExpression.THINKING,
        EyeExpression.BLINK, EyeExpression.WAKING_UP, EyeExpression.SHUT_DOWN,
        EyeExpression.SEARCHING, EyeExpression.LOVING, EyeExpression.CONFUSED,
        EyeExpression.DRIVE, EyeExpression.DEVELOPER,
    ]
    for expr in required:
        assert expr in EXPRESSIONS, f"Missing expression: {expr}"
    print("  OK test_all_expressions_present")


def test_expressions_have_valid_params():
    for expr, state in EXPRESSIONS.items():
        assert 0.0 <= state.scaleY <= 2.0, f"{expr}: scaleY out of range"
        assert 0.0 <= state.scaleX <= 2.0, f"{expr}: scaleX out of range"
        assert -1.0 <= state.look_x <= 1.0
        assert -1.0 <= state.look_y <= 1.0
        assert 0.0 <= state.squint <= 1.0
        assert -1.0 <= state.arch <= 1.0
        if state.eye_color:
            assert all(0 <= c <= 255 for c in state.eye_color)
    print("  OK test_expressions_have_valid_params")


def test_renderer_create():
    r = EyeRenderer(480, 320)
    assert r.left_eye is not None
    assert r.right_eye is not None
    assert r.width == 480
    assert r.height == 320
    print("  OK test_renderer_create")


def test_renderer_set_expression():
    r = EyeRenderer(480, 320)
    r.set_expression(EyeExpression.HAPPY, speed=6)
    assert r.get_expression() == EyeExpression.HAPPY
    print("  OK test_renderer_set_expression")


def test_renderer_render_all_expressions():
    r = EyeRenderer(480, 320)
    surf = pygame.Surface((480, 320))
    for expr in EyeExpression:
        r.set_expression(expr)
        for _ in range(5):
            r.update(0.016)
        r.render(surf)
    print("  OK test_renderer_render_all_expressions")


def test_renderer_blink():
    r = EyeRenderer(480, 320)
    surf = pygame.Surface((480, 320))
    r.trigger_blink()
    for _ in range(10):
        r.update(0.016)
        r.render(surf)
    assert r.get_expression() == EyeExpression.IDLE
    print("  OK test_renderer_blink")


def test_look_target():
    r = EyeRenderer(480, 320)
    r.set_look_target(0.5, -0.3)
    assert abs(r._look_target_x - 0.5) < 0.01
    assert abs(r._look_target_y - (-0.3)) < 0.01
    print("  OK test_look_target")


def test_look_at_face():
    r = EyeRenderer(480, 320)
    r.look_at_face(0.8, -0.5)
    assert abs(r._look_target_x - 0.48) < 0.01
    print("  OK test_look_at_face")


def test_eye_state_init():
    s = EyeState(scaleY=0.5, scaleX=1.2, squint=0.3, arch=0.7, eye_color=(255, 0, 0))
    assert s.scaleY == 0.5
    assert s.scaleX == 1.2
    assert s.squint == 0.3
    assert s.arch == 0.7
    assert s.eye_color == (255, 0, 0)
    print("  OK test_eye_state_init")


def test_expression_durations():
    for expr, state in EXPRESSIONS.items():
        assert state.duration > 0
        if expr == EyeExpression.BLINK:
            assert state.duration < 0.2
    print("  OK test_expression_durations")


def test_idle_random_look():
    r = EyeRenderer(480, 320)
    surf = pygame.Surface((480, 320))
    for _ in range(300):
        r.update(0.016)
        r.render(surf)
    look_x = r.left_eye.look_x
    assert -1.0 <= look_x <= 1.0
    print("  OK test_idle_random_look")


def test_wip_text():
    r = EyeRenderer(480, 320)
    surf = pygame.Surface((480, 320))
    r.wip_visible = True
    r.render(surf)
    r.wip_visible = False
    r.render(surf)
    print("  OK test_wip_text")


if __name__ == "__main__":
    test_all_expressions_present()
    test_expressions_have_valid_params()
    test_renderer_create()
    test_renderer_set_expression()
    test_renderer_render_all_expressions()
    test_renderer_blink()
    test_look_target()
    test_look_at_face()
    test_eye_state_init()
    test_expression_durations()
    test_idle_random_look()
    test_wip_text()
    print("\nTodos los tests de ojos pasados!")
