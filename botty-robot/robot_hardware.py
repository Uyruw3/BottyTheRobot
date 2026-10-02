"""GPIO drivers for the Botty differential-drive robot."""

import time


class RobotHardware:
    MOTOR_PINS = {
        "left": (17, 18, 13),
        "right": (22, 23, 24),
    }
    SONAR_TRIGGER = 5
    SONAR_ECHO = 6
    BUZZER_PIN = 26

    def __init__(self):
        self._gpio = None
        self._motor_pwm = {}
        self._buzzer_pwm = None
        self._simulated = True
        self._init_hardware()

    def _init_hardware(self):
        try:
            import RPi.GPIO as gpio
        except ImportError:
            print("  [Hardware] RPi.GPIO no disponible - modo simulacion")
            return

        gpio.setmode(gpio.BCM)
        try:
            for forward_pin, backward_pin, enable_pin in self.MOTOR_PINS.values():
                gpio.setup(forward_pin, gpio.OUT, initial=gpio.LOW)
                gpio.setup(backward_pin, gpio.OUT, initial=gpio.LOW)
                gpio.setup(enable_pin, gpio.OUT, initial=gpio.LOW)

            gpio.setup(self.SONAR_TRIGGER, gpio.OUT, initial=gpio.LOW)
            gpio.setup(self.SONAR_ECHO, gpio.IN)
            gpio.setup(self.BUZZER_PIN, gpio.OUT, initial=gpio.LOW)
            self._motor_pwm = {
                name: gpio.PWM(pins[2], 1000)
                for name, pins in self.MOTOR_PINS.items()
            }
            for pwm in self._motor_pwm.values():
                pwm.start(0)
        except Exception:
            gpio.cleanup()
            raise

        self._gpio = gpio
        self._simulated = False
        print("  [Hardware] GPIO y controladores iniciados")

    def _set_motor(self, side, speed):
        if self._simulated:
            return

        gpio = self._gpio
        forward_pin, backward_pin, _ = self.MOTOR_PINS[side]
        speed = max(-100, min(100, speed))
        gpio.output(forward_pin, speed > 0)
        gpio.output(backward_pin, speed < 0)
        self._motor_pwm[side].ChangeDutyCycle(abs(speed))

    def _drive(self, left_speed, right_speed):
        self._set_motor("left", left_speed)
        self._set_motor("right", right_speed)

    def motor_forward(self, speed=50):
        self._drive(speed, speed)

    def motor_backward(self, speed=50):
        self._drive(-speed, -speed)

    def motor_left(self, speed=50):
        self._drive(-speed, speed)

    def motor_right(self, speed=50):
        self._drive(speed, -speed)

    def motor_stop(self):
        self._drive(0, 0)

    def buzzer_on(self):
        if not self._simulated:
            self._gpio.output(self.BUZZER_PIN, self._gpio.HIGH)

    def buzzer_off(self):
        if self._buzzer_pwm:
            self._buzzer_pwm.stop()
            self._buzzer_pwm = None
        if not self._simulated:
            self._gpio.output(self.BUZZER_PIN, self._gpio.LOW)

    def buzzer_beep(self, freq=1000, duration=0.2):
        if self._simulated:
            return
        self.buzzer_off()
        self._buzzer_pwm = self._gpio.PWM(self.BUZZER_PIN, max(1, int(freq)))
        self._buzzer_pwm.start(50)
        try:
            time.sleep(max(0, duration))
        finally:
            self.buzzer_off()

    def get_distance(self) -> float:
        if self._simulated:
            return -1

        gpio = self._gpio
        gpio.output(self.SONAR_TRIGGER, gpio.LOW)
        time.sleep(0.000002)
        gpio.output(self.SONAR_TRIGGER, gpio.HIGH)
        time.sleep(0.00001)
        gpio.output(self.SONAR_TRIGGER, gpio.LOW)

        deadline = time.monotonic() + 0.03
        while gpio.input(self.SONAR_ECHO) == 0:
            if time.monotonic() >= deadline:
                return -1
        pulse_start = time.monotonic()
        while gpio.input(self.SONAR_ECHO) == 1:
            if time.monotonic() >= deadline:
                return -1
        return (time.monotonic() - pulse_start) * 17150

    def cleanup(self):
        if self._simulated:
            return
        self.motor_stop()
        self.buzzer_off()
        for pwm in self._motor_pwm.values():
            pwm.stop()
        self._gpio.cleanup()
        self._simulated = True
