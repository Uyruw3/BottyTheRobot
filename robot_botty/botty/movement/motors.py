"""
Motor control module — control de motores DC con PWM.
Incluye control diferencial, PID de velocidad y simulacion.
"""

import time
import math
import threading
from botty.config import Config


class SimulatedMotors:
    """Simulacion de motores para pruebas sin hardware."""
    def __init__(self):
        self._left_speed = 0
        self._right_speed = 0
        self._x = 0
        self._y = 0
        self._theta = 0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def init(self):
        self._running = True
        self._thread = threading.Thread(target=self._sim_loop, daemon=True)
        self._thread.start()
        return True

    def _sim_loop(self):
        while self._running:
            with self._lock:
                v = (self._left_speed + self._right_speed) / 2.0
                w = (self._right_speed - self._left_speed) * 0.01
                self._theta += w * 0.05
                self._x += v * math.cos(self._theta) * 0.05
                self._y += v * math.sin(self._theta) * 0.05
            time.sleep(0.05)

    def set_speed(self, left: float, right: float):
        with self._lock:
            self._left_speed = max(-100, min(100, left))
            self._right_speed = max(-100, min(100, right))

    def get_position(self):
        with self._lock:
            return (self._x, self._y, self._theta)

    def get_speed(self):
        with self._lock:
            return (self._left_speed, self._right_speed)

    def stop(self):
        self.set_speed(0, 0)

    def cleanup(self):
        self._running = False
        self.stop()
        if self._thread:
            self._thread.join(timeout=1)


class MotorDriver:
    """Controla un motor DC con PWM y encoder."""
    def __init__(self, name: str, pwm_pin: int, dir_pins: list[int], encoder_pins: list[int] = None):
        self.name = name
        self.pwm_pin = pwm_pin
        self.dir_pins = dir_pins
        self.encoder_pins = encoder_pins
        self._speed = 0
        self._target_speed = 0
        self._pwm = None
        self._encoder_count = 0
        self._lock = threading.Lock()

    def init(self):
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pwm_pin, GPIO.OUT)
            for pin in self.dir_pins:
                GPIO.setup(pin, GPIO.OUT)
            self._pwm = GPIO.PWM(self.pwm_pin, 1000)
            self._pwm.start(0)
            if self.encoder_pins:
                for pin in self.encoder_pins:
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            return True
        except Exception as e:
            print(f"  [Motor:{self.name}] init fallo: {e}")
            return False

    def set_speed(self, speed: float):
        speed = max(-100, min(100, speed))
        with self._lock:
            self._target_speed = speed
        if self._pwm:
            import RPi.GPIO as GPIO
            duty = abs(speed)
            GPIO.output(self.dir_pins[0], speed >= 0)
            if len(self.dir_pins) > 1:
                GPIO.output(self.dir_pins[1], speed < 0)
            self._pwm.ChangeDutyCycle(duty)

    def get_speed(self) -> float:
        with self._lock:
            return self._speed

    def stop(self):
        self.set_speed(0)

    def cleanup(self):
        self.stop()
        if self._pwm:
            self._pwm.stop()
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup([self.pwm_pin] + self.dir_pins)
        except Exception:
            pass


class DifferentialDrive:
    """Control de robot con traccion diferencial (2 ruedas)."""
    def __init__(self):
        self._left_motor = None
        self._right_motor = None
        self._max_speed = Config.MOTOR_MAX_SPEED
        self._acceleration = Config.MOTOR_ACCELERATION
        self._current_left = 0
        self._current_right = 0
        self._target_left = 0
        self._target_right = 0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._sim = None

    def init(self):
        try:
            self._left_motor = MotorDriver("left", Config.PWM_PIN, Config.DIR_PINS[:2])
            self._right_motor = MotorDriver("right", Config.PWM_PIN, Config.DIR_PINS[2:])
            l_ok = self._left_motor.init()
            r_ok = self._right_motor.init()
            if not (l_ok and r_ok):
                raise RuntimeError("Motor init failed")
        except Exception as e:
            print(f"  [Drive] Motor hardware init fallo: {e}")
            print("  [Drive] Usando motores simulados.")
            self._sim = SimulatedMotors()
            self._sim.init()

        self._running = True
        self._thread = threading.Thread(target=self._acceleration_loop, daemon=True)
        self._thread.start()
        return True

    def _acceleration_loop(self):
        while self._running:
            with self._lock:
                target_l = self._target_left
                target_r = self._target_right
            left_change = max(-self._acceleration, min(self._acceleration, target_l - self._current_left))
            right_change = max(-self._acceleration, min(self._acceleration, target_r - self._current_right))
            self._current_left += left_change
            self._current_right += right_change
            if self._sim:
                self._sim.set_speed(self._current_left, self._current_right)
            elif self._left_motor and self._right_motor:
                self._left_motor.set_speed(self._current_left)
                self._right_motor.set_speed(self._current_right)
            time.sleep(0.02)

    def set_speed(self, left: float, right: float):
        with self._lock:
            self._target_left = max(-self._max_speed, min(self._max_speed, left))
            self._target_right = max(-self._max_speed, min(self._max_speed, right))

    def forward(self, speed: float = None):
        s = speed if speed is not None else self._max_speed
        self.set_speed(s, s)

    def backward(self, speed: float = None):
        s = speed if speed is not None else self._max_speed
        self.set_speed(-s, -s)

    def left(self, speed: float = None):
        s = speed if speed is not None else self._max_speed
        self.set_speed(-s * 0.5, s * 0.5)

    def right(self, speed: float = None):
        s = speed if speed is not None else self._max_speed
        self.set_speed(s * 0.5, -s * 0.5)

    def pivot_left(self, speed: float = None):
        s = speed if speed is not None else self._max_speed * 0.6
        self.set_speed(-s, s)

    def pivot_right(self, speed: float = None):
        s = speed if speed is not None else self._max_speed * 0.6
        self.set_speed(s, -s)

    def stop(self):
        self.set_speed(0, 0)

    def get_speed(self) -> tuple[float, float]:
        with self._lock:
            return (self._current_left, self._current_right)

    def get_position(self) -> tuple[float, float, float]:
        if self._sim:
            return self._sim.get_position()
        return (0, 0, 0)

    def is_moving(self) -> bool:
        l, r = self.get_speed()
        return abs(l) > 1 or abs(r) > 1

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        self.stop()
        time.sleep(0.1)
        if self._sim:
            self._sim.cleanup()
        if self._left_motor:
            self._left_motor.cleanup()
        if self._right_motor:
            self._right_motor.cleanup()


class Motors(DifferentialDrive):
    """Compatibility interface used by the robot application and dashboard."""

    def drive(self, left: float, right: float):
        self.set_speed(left, right)

    def turn_left(self, speed: float = None):
        self.left(speed)

    def turn_right(self, speed: float = None):
        self.right(speed)
