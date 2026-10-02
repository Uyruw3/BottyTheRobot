"""
Tests for web dashboard module.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from botty.web import WebDashboard


def test_web_create_no_flask():
    w = WebDashboard()
    assert w is not None
    print("  OK test_web_create_no_flask")


def test_web_start_no_flask():
    w = WebDashboard()
    result = w.start()
    assert result == False
    print("  OK test_web_start_no_flask")


def test_web_stop():
    w = WebDashboard()
    w.stop()
    print("  OK test_web_stop")


def test_web_push_frame_no_cv():
    w = WebDashboard()
    w.push_frame(None)
    print("  OK test_web_push_frame_no_cv")


def test_web_log():
    w = WebDashboard()
    w._log("test message")
    w._log("another message")
    assert w._log_queue.qsize() == 2
    print("  OK test_web_log")


def test_web_log_full():
    w = WebDashboard()
    for i in range(150):
        w._log(f"msg {i}")
    assert w._log_queue.qsize() <= 100
    print("  OK test_web_log_full")


def test_web_frame_queue():
    w = WebDashboard()
    assert w._frame_queue.maxsize == 10
    print("  OK test_web_frame_queue")


def test_web_generate_frames():
    w = WebDashboard()
    gen = w._generate_frames()
    assert gen is not None
    print("  OK test_web_generate_frames")


def test_web_multiple_starts():
    w = WebDashboard()
    w.stop()
    w.stop()
    print("  OK test_web_multiple_starts")


if __name__ == "__main__":
    test_web_create_no_flask()
    test_web_start_no_flask()
    test_web_stop()
    test_web_push_frame_no_cv()
    test_web_log()
    test_web_log_full()
    test_web_frame_queue()
    test_web_generate_frames()
    test_web_multiple_starts()
    print("\nTodos los tests de web pasados!")
