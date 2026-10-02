"""
Ultrasonic sensors — HC-SR04 para deteccion de obstaculos.
Frontal, izquierdo y derecho. Incluye sensores virtuales para simulacion.
"""

import time
import math
import threading
import random
from botty.config import Config


class SimulatedUltrasonic:
    """Sensor ultrasonico simulado para pruebas sin hardware."""
    def __init__(self, position: str = "front"):
        self.position = position
        self._distance = random.uniform(20, 200)
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def init(self):
        self._running = True
        self._thread = threading.Thread(target=self._simulate_loop, daemon=True)
        self._thread.start()
        return True

    def _simulate_loop(self):
        while self._running:
            vx = random.gauss(0, 2)
            vy = random.gauss(0, 1.5)
            with self._lock:
                self._distance = max(2, min(400, self._distance + vx))
                self._distance += math.sin(time.time() * 0.5 + hash(self.position) * 0.1) * 1.5
            time.sleep(0.05)

    @property
    def distance(self) -> float:
        with self._lock:
            return max(0, self._distance)

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)


class UltrasonicSensor:
    def __init__(self, trigger_pin: int, echo_pin: int, position: str = "front"):
        self.trigger = trigger_pin
        self.echo = echo_pin
        self.position = position
        self._distance = 999.0
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._readings = []
        self._max_readings = 10
        self._obstacle_history = []
        self._last_obstacle_time = 0

    def init(self):
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger, GPIO.OUT)
            GPIO.setup(self.echo, GPIO.IN)
            GPIO.output(self.trigger, False)
            time.sleep(0.5)
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"  [Ultrasonic:{self.position}] init fallo, usando simulado: {e}")
            sim = SimulatedUltrasonic(self.position)
            sim.init()
            self._sim = sim
            self._running = True
            self._thread = threading.Thread(target=self._sim_read_loop, daemon=True)
            self._thread.start()
            return True

    def _sim_read_loop(self):
        while self._running:
            with self._lock:
                self._distance = self._sim.distance
            time.sleep(0.05)

    def _loop(self):
        import RPi.GPIO as GPIO
        while self._running:
            dist = self._measure(GPIO)
            with self._lock:
                self._distance = dist
                self._readings.append(dist)
                if len(self._readings) > self._max_readings:
                    self._readings.pop(0)
            if dist < 20:
                self._obstacle_history.append(time.time())
                if len(self._obstacle_history) > 10:
                    self._obstacle_history.pop(0)
                self._last_obstacle_time = time.time()
            time.sleep(0.05)

    def _measure(self, GPIO) -> float:
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)
        timeout = time.time() + 0.05
        while GPIO.input(self.echo) == 0:
            if time.time() > timeout:
                return 999.0
        start = time.time()
        while GPIO.input(self.echo) == 1:
            if time.time() > start + 0.05:
                return 999.0
        elapsed = time.time() - start
        dist = elapsed * 17150.0
        return max(0, min(400, dist))

    @property
    def distance(self) -> float:
        with self._lock:
            return self._distance

    def filtered_distance(self) -> float:
        with self._lock:
            if not self._readings:
                return self._distance
            valid = [d for d in self._readings if d < 400]
            if not valid:
                return 999.0
            return sum(valid) / len(valid)

    def is_obstacle_detected(self, threshold: float = 30.0) -> bool:
        return self.distance < threshold

    def obstacle_frequency(self, window: float = 5.0) -> float:
        now = time.time()
        recent = [t for t in self._obstacle_history if now - t < window]
        return len(recent) / window if recent else 0.0

    def time_since_last_obstacle(self) -> float:
        if not self._last_obstacle_time:
            return 999.0
        return time.time() - self._last_obstacle_time

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if hasattr(self, "_sim"):
            self._sim.cleanup()
        else:
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup([self.trigger, self.echo])
            except Exception:
                pass


class SonarArray:
    """Gestiona los 3 sensores ultrasonicos con capacidades adicionales."""
    def __init__(self):
        self.sensors = {}
        self.pins = Config.ULTRASONIC_PINS
        self._ready = False
        self._avoidance_active = False
        self._avoidance_thread = None

    def init(self):
        cfg = self.pins
        positions = [
            ("front", cfg["front_trigger"], cfg["front_echo"]),
            ("left", cfg["left_trigger"], cfg["left_echo"]),
            ("right", cfg["right_trigger"], cfg["right_echo"]),
        ]
        for name, trig, echo in positions:
            s = UltrasonicSensor(trig, echo, name)
            if s.init():
                self.sensors[name] = s
                print(f"  [Sonar] {name.capitalize()} listo (T:{trig} E:{echo})")
        self._ready = len(self.sensors) > 0
        return self._ready

    @property
    def ready(self) -> bool:
        return self._ready

    def read(self) -> dict[str, float]:
        return {name: s.distance for name, s in self.sensors.items()}

    def read_filtered(self) -> dict[str, float]:
        return {name: s.filtered_distance() for name, s in self.sensors.items()}

    def closest(self) -> tuple[str, float]:
        readings = self.read()
        if not readings:
            return ("none", 999.0)
        return min(readings.items(), key=lambda x: x[1])

    def any_closer_than(self, threshold: float) -> bool:
        return any(d < threshold for d in self.read().values())

    def safe_direction(self) -> str:
        """Retorna la direccion mas despejada: front, left, right."""
        readings = self.read_filtered()
        if not readings:
            return "front"
        safest = max(readings.items(), key=lambda x: x[1])
        return safest[0]

    def all_clear(self, threshold: float = 40.0) -> bool:
        return all(d > threshold for d in self.read().values())

    def obstacle_map(self) -> dict[str, str]:
        readings = self.read()
        result = {}
        for name, dist in readings.items():
            if dist < 15:
                result[name] = "critical"
            elif dist < 30:
                result[name] = "warning"
            elif dist < 60:
                result[name] = "caution"
            else:
                result[name] = "clear"
        return result

    def start_avoidance(self, callback):
        self._avoidance_active = True
        def _loop():
            while self._avoidance_active:
                readings = self.read()
                for name, dist in readings.items():
                    if dist < 15:
                        callback("emergency_stop", {"sensor": name, "distance": dist})
                    elif dist < 25:
                        callback("obstacle_close", {"sensor": name, "distance": dist})
                time.sleep(0.1)
        self._avoidance_thread = threading.Thread(target=_loop, daemon=True)
        self._avoidance_thread.start()

    def stop_avoidance(self):
        self._avoidance_active = False

    def cleanup(self):
        self.stop_avoidance()
        for s in self.sensors.values():
            s.cleanup()
        self._ready = False
