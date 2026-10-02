"""
Face detection and recognition module.
Detecta caras con OpenCV y reconoce identidades con face_recognition.
"""

import os
import cv2
import numpy as np
from pathlib import Path

from botty.config import Config


class FaceRecognizer:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.face_cascade = None
        self._loaded = False
        self.ready = False

    def load_known_faces(self):
        known_dir = Path(Config.KNOWN_FACES_DIR)
        if not known_dir.exists():
            known_dir.mkdir(parents=True, exist_ok=True)
            self.ready = True
            return

        try:
            import face_recognition as fr
        except ImportError:
            print("  [FaceRec] face_recognition no disponible")
            return

        for img_path in known_dir.glob("*.*"):
            if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            try:
                image = fr.load_image_file(str(img_path))
                encodings = fr.face_encodings(image)
                if encodings:
                    name = img_path.stem
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(name)
                    print(f"  -> Cargada cara conocida: {name}")
            except Exception as e:
                print(f"  ! Error cargando {img_path.name}: {e}")

        print(f"  Total caras conocidas: {len(self.known_names)}")
        self._loaded = True
        self.ready = True

    def detect_faces(self, frame: np.ndarray) -> list[dict]:
        if frame is None or frame.size == 0:
            return []

        faces = []
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if self.face_cascade is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

        detected = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )

        for (x, y, w, h) in detected:
            # Scale back to original size
            x, y, w, h = x * 2, y * 2, w * 2, h * 2
            faces.append({
                "bbox": (x, y, w, h),
                "center": (x + w // 2, y + h // 2),
            })

        return faces

    def recognize(self, frame: np.ndarray, faces: list[dict]) -> list[dict]:
        if not self._loaded or not faces:
            return faces

        import face_recognition as fr

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        for face in faces:
            x, y, w, h = face["bbox"]
            face_roi = rgb[y:y + h, x:x + w]
            if face_roi.size == 0:
                continue
            encodings = fr.face_encodings(frame, [(y, x + w, y + h, x)])
            if not encodings:
                face["name"] = "Desconocido"
                continue

            matches = fr.compare_faces(
                self.known_encodings, encodings[0],
                tolerance=Config.RECOGNITION_TOLERANCE
            )
            if any(matches):
                idx = matches.index(True)
                face["name"] = self.known_names[idx]
            else:
                face["name"] = "Desconocido"

        return faces

    def draw_faces(self, frame: np.ndarray, faces: list[dict]):
        for face in faces:
            x, y, w, h = face["bbox"]
            name = face.get("name", "?")
            color = (0, 255, 0) if name != "Desconocido" else (0, 200, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, name, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
