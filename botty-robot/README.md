# Botty Robot Hardware Console

This independent console lives in the [`BottyRobot`](https://github.com/Uyruw3/BottyRobot)
repository and tests the physical Botty's motors, sonar, and buzzer. It does
not import or require the Windows desktop edition.

## Requirements and wiring

- Raspberry Pi with Raspberry Pi OS and Python 3.10+
- L298N-compatible dual H-bridge, HC-SR04-compatible ultrasonic sensor, and
  active or passive buzzer
- `RPi.GPIO` installed on the Pi (`python -m pip install RPi.GPIO`)
- GPIO assignments use **BCM numbering**:

| Function | BCM pins |
| --- | --- |
| Left motor direction / PWM enable | 17, 18 / 13 |
| Right motor direction / PWM enable | 22, 23 / 24 |
| Sonar trigger / echo | 5 / 6 |
| Buzzer | 26 |

Use an external motor power supply and connect grounds. **Never connect the
HC-SR04's 5 V echo output directly to a Raspberry Pi GPIO**; use a voltage
divider or logic-level shifter. Verify your driver pinout and raise the robot's
wheels before testing movement. Wiring and voltage conversion are not included.

## Install and run

```bash
cd botty-robot
python -m pip install -e .
botty-robot
```

The console accepts `forward`, `backward`, `left`, `right`, `stop`, `distance`,
`beep`, `help`, and `quit`. Movement commands stop automatically after 0.3
seconds by default; a custom duration can be set up to a 2-second maximum.
Without `RPi.GPIO`, it starts in simulation mode and does not control hardware.

## Tests

```bash
python -m pip install pytest
python -m pytest
```
