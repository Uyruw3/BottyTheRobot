"""
Object detection — detecta pies, piernas, objetos en movimiento
y personas con HOG + OpenCV.
"""

import cv2
import numpy as np
from botty.config import Config


class ObjectDetector:
    def __init__(self):
        self.hog = None
        self._ready = False
        self._prev_frame = None

    def init(self):
        try:
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self._ready = True
            print("  [ObjectDetector] HOG people detector listo")
            return True
        except Exception as e:
            print(f"  [ObjectDetector] Error: {e}")
            return False

    @property
    def ready(self) -> bool:
        return self._ready

    def detect_people(self, frame: np.ndarray) -> list[dict]:
        """Detecta personas/piernas en el frame.
        Retorna lista de {bbox, center, distance_estimate}."""
        if not self._ready:
            return []

        results = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # People detection
        rects, _ = self.hog.detectMultiScale(
            gray, winStride=(4, 4), padding=(8, 8), scale=1.05
        )

        for (x, y, w, h) in rects:
            # Person height in pixels relative to frame
            person_height_px = h
            # Rough distance estimate (shorter = farther)
            dist_estimate = 500.0 / max(person_height_px, 1)
            results.append({
                "bbox": (x, y, w, h),
                "center": (x + w // 2, y + h // 2),
                "distance_estimate": dist_estimate,
                "type": "person",
                "feet_y": y + h,
            })

        return results

    def detect_motion(self, frame: np.ndarray, threshold: float = 30.0,
                      min_area: int = 500) -> list[dict]:
        """Detecta objetos en movimiento por diferencia de frames.
        Retorna lista de {bbox, center, area}."""
        if self._prev_frame is None:
            self._prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        diff = cv2.absdiff(self._prev_frame, gray)
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        results = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            results.append({
                "bbox": (x, y, w, h),
                "center": (x + w // 2, y + h // 2),
                "area": area,
                "type": "moving_object",
            })

        self._prev_frame = gray
        return results

    def detect_legs_and_feet(self, frame: np.ndarray) -> list[dict]:
        """Busca piernas/pies en la mitad inferior del frame.
        Usa la deteccion de personas y extrae la region inferior."""
        people = self.detect_people(frame)
        legs = []
        for p in people:
            x, y, w, h = p["bbox"]
            # La mitad inferior de la persona son las piernas
            leg_y = y + h // 2
            leg_h = h // 2
            legs.append({
                "bbox": (x, leg_y, w, leg_h),
                "center": (x + w // 2, leg_y + leg_h // 2),
                "distance_estimate": p["distance_estimate"],
                "type": "legs_feet",
            })
        return legs
