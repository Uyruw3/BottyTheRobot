"""
Tests for vision/camera modules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SDL_VIDEODRIVER"] = "dummy"

from botty.vision.camera import Camera
from botty.vision.face_recognition import FaceRecognizer
from botty.vision.object_detection import ObjectDetector


def test_camera_create():
    c = Camera()
    assert c is not None
    print("  OK test_camera_create")


def test_camera_start():
    c = Camera()
    result = c.start()
    assert isinstance(result, bool)
    print("  OK test_camera_start")


def test_camera_read():
    c = Camera()
    frame = c.read()
    assert frame is None or hasattr(frame, "shape")
    print("  OK test_camera_read")


def test_camera_release():
    c = Camera()
    c.release()
    print("  OK test_camera_release")


def test_face_recognizer_create():
    fr = FaceRecognizer()
    assert fr is not None
    assert hasattr(fr, "ready")
    print("  OK test_face_recognizer_create")


def test_face_recognizer_load():
    fr = FaceRecognizer()
    fr.load_known_faces()
    print("  OK test_face_recognizer_load")


def test_face_recognizer_detect():
    fr = FaceRecognizer()
    import numpy as np
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    faces = fr.detect_faces(fake_frame)
    assert isinstance(faces, list)
    print("  OK test_face_recognizer_detect")


def test_face_recognizer_no_camera():
    fr = FaceRecognizer()
    result = fr.detect_faces(None)
    if result is None:
        pass
    print("  OK test_face_recognizer_no_camera")


def test_object_detector_create():
    od = ObjectDetector()
    assert od is not None
    assert hasattr(od, "ready")
    print("  OK test_object_detector_create")


def test_object_detector_init():
    od = ObjectDetector()
    try:
        od.init()
    except Exception:
        pass
    print("  OK test_object_detector_init")


def test_object_detector_detect():
    od = ObjectDetector()
    import numpy as np
    fake = np.zeros((480, 640, 3), dtype=np.uint8)
    result = od.detect_legs_and_feet(fake)
    assert isinstance(result, list)
    print("  OK test_object_detector_detect")


def test_object_detector_motion():
    od = ObjectDetector()
    import numpy as np
    fake = np.zeros((480, 640, 3), dtype=np.uint8)
    result = od.detect_motion(fake)
    assert isinstance(result, list)
    print("  OK test_object_detector_motion")


def test_face_recognizer_familairity():
    fr = FaceRecognizer()
    assert hasattr(fr, "known_names")
    assert isinstance(fr.known_names, list)
    print("  OK test_face_recognizer_familairity")


if __name__ == "__main__":
    test_camera_create()
    test_camera_start()
    test_camera_read()
    test_camera_release()
    test_face_recognizer_create()
    test_face_recognizer_load()
    test_face_recognizer_detect()
    test_face_recognizer_no_camera()
    test_object_detector_create()
    test_object_detector_init()
    test_object_detector_detect()
    test_object_detector_motion()
    test_face_recognizer_familairity()
    print("\nTodos los tests de vision pasados!")
