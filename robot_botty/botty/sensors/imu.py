"""
IMU sensor module — MPU6050 accelerometer and gyroscope.
Includes virtual simulation for testing.
"""

import time
import math
import random
import threading
import numpy as np


class SimulatedIMU:
    """IMU simulation for testing without hardware."""
    def __init__(self):
        self._ax = 0.0
        self._ay = 0.0
        self._az = 9.81
        self._gx = 0.0
        self._gy = 0.0
        self._gz = 0.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._temperature = 25.0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._time = 0

    def init(self):
        self._running = True
        self._thread = threading.Thread(target=self._simulate, daemon=True)
        self._thread.start()
        return True

    def _simulate(self):
        while self._running:
            self._time += 0.01
            noise_a = random.gauss(0, 0.05)
            noise_g = random.gauss(0, 0.01)
            slow_drift = math.sin(self._time * 0.1) * 0.2
            with self._lock:
                self._ax = noise_a + slow_drift
                self._ay = noise_a * 0.7
                self._az = 9.81 + random.gauss(0, 0.03)
                self._gx = noise_g + math.sin(self._time * 0.3) * 0.05
                self._gy = noise_g * 0.8
                self._gz = noise_g * 1.2
                self._roll = math.atan2(self._ay, self._az)
                self._pitch = math.atan2(-self._ax, math.sqrt(self._ay**2 + self._az**2))
                self._yaw += self._gz * 0.01
                self._temperature = 25.0 + math.sin(self._time * 0.05) * 0.5
            time.sleep(0.01)

    def get_acceleration(self):
        with self._lock:
            return (self._ax, self._ay, self._az)

    def get_gyroscope(self):
        with self._lock:
            return (self._gx, self._gy, self._gz)

    def get_angles(self):
        with self._lock:
            return (self._roll, self._pitch, self._yaw)

    def get_temperature(self):
        with self._lock:
            return self._temperature

    def get_all(self):
        with self._lock:
            return {
                "ax": self._ax, "ay": self._ay, "az": self._az,
                "gx": self._gx, "gy": self._gy, "gz": self._gz,
                "roll": self._roll, "pitch": self._pitch, "yaw": self._yaw,
                "temp": self._temperature,
                "temperature": self._temperature,
            }

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)


class MPU6050:
    """MPU6050 accelerometer and gyroscope sensor."""
    def __init__(self, address=0x68, bus=1):
        self.address = address
        self.bus = bus
        self._accel_scale = 2.0
        self._gyro_scale = 250.0
        self._ax = 0.0
        self._ay = 0.0
        self._az = 9.81
        self._gx = 0.0
        self._gy = 0.0
        self._gz = 0.0
        self._temperature = 25.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._device = None
        self._sim = None

    def init(self):
        try:
            import smbus
            self._device = smbus.SMBus(self.bus)
            self._device.write_byte_data(self.address, 0x6B, 0)
            self._device.write_byte_data(self.address, 0x1C, 0x00)
            self._device.write_byte_data(self.address, 0x1B, 0x00)
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"  [IMU] MPU6050 init fallo: {e}")
            print("  [IMU] Usando IMU simulado.")
            self._sim = SimulatedIMU()
            self._sim.init()
            self._running = True
            self._thread = threading.Thread(target=self._sim_read_loop, daemon=True)
            self._thread.start()
            return True

    def _sim_read_loop(self):
        while self._running:
            data = self._sim.get_all()
            with self._lock:
                self._ax = data["ax"]
                self._ay = data["ay"]
                self._az = data["az"]
                self._gx = data["gx"]
                self._gy = data["gy"]
                self._gz = data["gz"]
                self._roll = data["roll"]
                self._pitch = data["pitch"]
                self._yaw = data["yaw"]
                self._temperature = data["temp"]
            time.sleep(0.01)

    def _read_loop(self):
        while self._running:
            try:
                data = self._device.read_i2c_block_data(self.address, 0x3B, 14)
                ax_raw = self._combine_bytes(data[0], data[1])
                ay_raw = self._combine_bytes(data[2], data[3])
                az_raw = self._combine_bytes(data[4], data[5])
                temp_raw = self._combine_bytes(data[6], data[7])
                gx_raw = self._combine_bytes(data[8], data[9])
                gy_raw = self._combine_bytes(data[10], data[11])
                gz_raw = self._combine_bytes(data[12], data[13])
                with self._lock:
                    self._ax = ax_raw / 16384.0 * self._accel_scale
                    self._ay = ay_raw / 16384.0 * self._accel_scale
                    self._az = az_raw / 16384.0 * self._accel_scale
                    self._gx = gx_raw / 131.0 * self._gyro_scale
                    self._gy = gy_raw / 131.0 * self._gyro_scale
                    self._gz = gz_raw / 131.0 * self._gyro_scale
                    self._temperature = temp_raw / 340.0 + 36.53
                    self._roll = math.atan2(self._ay, self._az)
                    self._pitch = math.atan2(-self._ax, math.sqrt(self._ay**2 + self._az**2))
                    self._yaw += self._gz * 0.01
            except Exception as e:
                print(f"  [IMU] Error de lectura: {e}")
            time.sleep(0.01)

    def _combine_bytes(self, high, low):
        val = (high << 8) | low
        if val >= 0x8000:
            val -= 0x10000
        return val

    def get_acceleration(self):
        with self._lock:
            return (self._ax, self._ay, self._az)

    def get_gyroscope(self):
        with self._lock:
            return (self._gx, self._gy, self._gz)

    def get_angles(self):
        with self._lock:
            return (self._roll, self._pitch, self._yaw)

    def get_temperature(self):
        with self._lock:
            return self._temperature

    def get_all(self):
        with self._lock:
            return {
                "ax": round(self._ax, 3),
                "ay": round(self._ay, 3),
                "az": round(self._az, 3),
                "gx": round(self._gx, 3),
                "gy": round(self._gy, 3),
                "gz": round(self._gz, 3),
                "roll": round(math.degrees(self._roll), 1),
                "pitch": round(math.degrees(self._pitch), 1),
                "yaw": round(math.degrees(self._yaw), 1),
                "temperature": round(self._temperature, 1),
            }

    def is_moving(self, threshold=0.1):
        ax, ay, az = self.get_acceleration()
        total = math.sqrt(ax**2 + ay**2 + (az - 9.81)**2)
        return total > threshold

    def is_level(self, threshold=5.0):
        roll, pitch, yaw = self.get_angles()
        return abs(math.degrees(roll)) < threshold and abs(math.degrees(pitch)) < threshold

    def get_orientation(self):
        roll, pitch, yaw = self.get_angles()
        r = math.degrees(roll)
        p = math.degrees(pitch)
        if abs(r) < 15 and abs(p) < 15:
            return "level"
        if r > 15:
            return "tilted_right"
        if r < -15:
            return "tilted_left"
        if p > 15:
            return "tilted_forward"
        if p < -15:
            return "tilted_backward"
        return "unknown"

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if self._sim:
            self._sim.cleanup()
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
