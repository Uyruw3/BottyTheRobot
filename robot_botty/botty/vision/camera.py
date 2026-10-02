"""
Camera module — captura video desde camara USB o Pi Camera.
Soporta OpenCV, Picamera2, y modos de deteccion.
"""

import cv2
import numpy as np
from botty.config import Config


class Camera:
    def __init__(self):
        self.cap = None
        self.running = False
        self.last_frame = None
        self._width = Config.CAMERA_WIDTH
        self._height = Config.CAMERA_HEIGHT
        self._fps = Config.CAMERA_FRAMERATE
        self._brightness = 0.5
        self._contrast = 0.5
        self._flip_h = False
        self._flip_v = False
        self._recording = False
        self._video_writer = None

    def start(self):
        if Config.CAMERA_BACKEND == "picamera2":
            self._start_picamera2()
        else:
            self.cap = cv2.VideoCapture(Config.CAMERA_ID)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            self.cap.set(cv2.CAP_PROP_FPS, self._fps)
            if not self.cap.isOpened():
                print(f"  [Camera] Error: No se pudo abrir camara {Config.CAMERA_ID}")
                return False
        self.running = True
        return True

    def _start_picamera2(self):
        try:
            from picamera2 import Picamera2
            self.cap = Picamera2()
            config = self.cap.create_video_configuration(
                main={"size": (self._width, self._height)},
                controls={"FrameRate": self._fps}
            )
            self.cap.configure(config)
            self.cap.start()
        except ImportError:
            raise RuntimeError("picamera2 no esta instalado")

    def read(self) -> np.ndarray | None:
        if self.cap is None or not self.running:
            return None
        try:
            if Config.CAMERA_BACKEND == "picamera2":
                frame = self.cap.capture_array()
                self.last_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                ret, frame = self.cap.read()
                if not ret:
                    return None
                self.last_frame = frame
            if self._flip_h or self._flip_v:
                flip_code = (1 if self._flip_h else 0) | (0 if self._flip_v else 0)
                if self._flip_h and self._flip_v:
                    flip_code = -1
                self.last_frame = cv2.flip(self.last_frame, flip_code)
            if self._recording and self._video_writer:
                self._video_writer.write(self.last_frame)
            return self.last_frame
        except Exception as e:
            print(f"  [Camera] Error reading frame: {e}")
            return None

    def get_frame_jpeg(self) -> bytes | None:
        frame = self.read()
        if frame is None:
            return None
        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            return None
        return buffer.tobytes()

    def set_resolution(self, width: int, height: int):
        self._width = width
        self._height = height
        if self.cap and Config.CAMERA_BACKEND != "picamera2":
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def set_brightness(self, val: float):
        self._brightness = max(0.0, min(1.0, val))
        if self.cap and Config.CAMERA_BACKEND != "picamera2":
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self._brightness * 255)

    def set_contrast(self, val: float):
        self._contrast = max(0.0, min(1.0, val))
        if self.cap and Config.CAMERA_BACKEND != "picamera2":
            self.cap.set(cv2.CAP_PROP_CONTRAST, self._contrast * 255)

    def set_flip(self, horizontal: bool = False, vertical: bool = False):
        self._flip_h = horizontal
        self._flip_v = vertical

    def start_recording(self, output_path: str):
        if self._recording:
            self.stop_recording()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._video_writer = cv2.VideoWriter(output_path, fourcc, self._fps, (self._width, self._height))
        self._recording = True
        print(f"  [Camera] Recording started: {output_path}")

    def stop_recording(self):
        self._recording = False
        if self._video_writer:
            self._video_writer.release()
            self._video_writer = None
            print("  [Camera] Recording stopped")

    def take_photo(self, output_path: str) -> bool:
        frame = self.read()
        if frame is None:
            return False
        return cv2.imwrite(output_path, frame)

    def release(self):
        self.running = False
        if self._recording:
            self.stop_recording()
        if self.cap is not None:
            if Config.CAMERA_BACKEND == "picamera2":
                self.cap.stop()
            else:
                self.cap.release()
        print("  [Camera] Released")
