"""
Temperature and humidity sensor module — DHT11/DHT22.
Includes virtual simulation for testing.
"""

import time
import random
import math
import threading


class SimulatedDHT:
    """Simulates DHT temperature/humidity sensor."""
    def __init__(self, pin):
        self.pin = pin
        self._temperature = 22.0
        self._humidity = 55.0
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._time_offset = 0

    def init(self):
        self._running = True
        self._thread = threading.Thread(target=self._simulate, daemon=True)
        self._thread.start()
        return True

    def _simulate(self):
        while self._running:
            self._time_offset += 0.1
            temp_drift = math.sin(self._time_offset * 0.05) * 3.0
            hum_drift = math.sin(self._time_offset * 0.03) * 10.0
            with self._lock:
                self._temperature = 22.0 + temp_drift + random.gauss(0, 0.5)
                self._humidity = 55.0 + hum_drift + random.gauss(0, 1)
                self._temperature = max(-10, min(60, self._temperature))
                self._humidity = max(0, min(100, self._humidity))
            time.sleep(1)

    def read(self):
        with self._lock:
            return (self._temperature, self._humidity)

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)


class DHT11:
    """DHT11 temperature and humidity sensor."""
    def __init__(self, pin):
        self.pin = pin
        self._temperature = 0.0
        self._humidity = 0.0
        self._last_read = 0
        self._read_interval = 2.0
        self._lock = threading.Lock()
        self._sim = None

    def init(self):
        try:
            import Adafruit_DHT
            self._sensor = Adafruit_DHT.DHT11
            self._read_func = Adafruit_DHT.read_retry
            return True
        except ImportError:
            print(f"  [DHT11] Adafruit_DHT no instalado. Usando simulado.")
            self._sim = SimulatedDHT(self.pin)
            return self._sim.init()

    def read(self):
        now = time.time()
        if now - self._last_read < self._read_interval:
            with self._lock:
                return (self._temperature, self._humidity)
        if self._sim:
            temp, hum = self._sim.read()
        else:
            try:
                hum, temp = self._read_func(self._sensor, self.pin)
                if hum is None or temp is None:
                    return (self._temperature, self._humidity)
            except Exception as e:
                print(f"  [DHT11] Read error: {e}")
                return (self._temperature, self._humidity)
        with self._lock:
            self._temperature = temp
            self._humidity = hum
            self._last_read = now
        return (temp, hum)

    def get_temperature(self):
        self.read()
        with self._lock:
            return self._temperature

    def get_humidity(self):
        self.read()
        with self._lock:
            return self._humidity

    def get_heat_index(self):
        temp, hum = self.read()
        if temp is None or hum is None:
            return None
        c1 = -8.78469475556
        c2 = 1.61139411989
        c3 = 2.33854883889
        c4 = -0.1461160509
        c5 = -0.0123080944
        c6 = -0.0164248278
        c7 = 0.002211732
        c8 = 0.00072546
        c9 = -0.000003582
        T = temp * 9.0 / 5.0 + 32
        R = hum
        hi = (c1 + c2 * T + c3 * R + c4 * T * R + c5 * T * T +
              c6 * R * R + c7 * T * T * R + c8 * T * R * R + c9 * T * T * R * R)
        return (hi - 32) * 5.0 / 9.0

    def get_dew_point(self):
        temp, hum = self.read()
        if temp is None or hum is None:
            return None
        a = 17.27
        b = 237.7
        gamma = (a * temp) / (b + temp) + math.log(hum / 100.0)
        return (b * gamma) / (a - gamma)

    def cleanup(self):
        if self._sim:
            self._sim.cleanup()


class DHT22(DHT11):
    """DHT22 temperature and humidity sensor (more precise)."""
    def init(self):
        try:
            import Adafruit_DHT
            self._sensor = Adafruit_DHT.DHT22
            self._read_func = Adafruit_DHT.read_retry
            return True
        except ImportError:
            print(f"  [DHT22] Adafruit_DHT no instalado. Usando simulado.")
            self._sim = SimulatedDHT(self.pin)
            return self._sim.init()


class TemperatureManager:
    """Manages temperature and humidity monitoring."""
    def __init__(self, pin=4, sensor_type="dht11"):
        self.pin = pin
        self.sensor_type = sensor_type
        self._sensor = None
        self._readings = []
        self._max_readings = 100
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def init(self):
        if self.sensor_type == "dht22":
            self._sensor = DHT22(self.pin)
        else:
            self._sensor = DHT11(self.pin)
        if self._sensor.init():
            self._running = True
            self._thread = threading.Thread(target=self._logging_loop, daemon=True)
            self._thread.start()
            return True
        return False

    def _logging_loop(self):
        while self._running:
            temp, hum = self._sensor.read()
            with self._lock:
                self._readings.append({"temp": temp, "hum": hum, "time": time.time()})
                if len(self._readings) > self._max_readings:
                    self._readings.pop(0)
            time.sleep(10)

    def get_current(self):
        return self._sensor.read() if self._sensor else (None, None)

    def get_statistics(self):
        with self._lock:
            if not self._readings:
                return {}
            temps = [r["temp"] for r in self._readings]
            hums = [r["hum"] for r in self._readings]
            return {
                "temp_avg": sum(temps) / len(temps),
                "temp_min": min(temps),
                "temp_max": max(temps),
                "hum_avg": sum(hums) / len(hums),
                "hum_min": min(hums),
                "hum_max": max(hums),
                "readings": len(self._readings),
            }

    def cleanup(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._sensor:
            self._sensor.cleanup()
